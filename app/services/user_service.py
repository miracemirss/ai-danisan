# app/services/user_service.py

from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app import models, schemas
from app.services.audit_log_service import AuditLogService
from app.core.security import get_password_hash


class UserService:

    @staticmethod
    def _get_user_in_tenant_or_404(
        db: Session,
        tenant_id: int,
        user_id: int,
    ) -> models.User:
        """
        Yardımcı Fonksiyon: Belirtilen ID'li kullanıcıyı, belirtilen tenant içinde arar.
        Bulamazsa 404 hatası fırlatır.
        """
        user = (
            db.query(models.User)
            .filter(
                models.User.id == user_id,
                models.User.tenant_id == tenant_id,
            )
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in this tenant.",
            )
        return user

    @staticmethod
    def list_users(db: Session, tenant_id: int) -> List[models.User]:
        """
        Tenant'a ait tüm kullanıcıları listeler.
        """
        return db.query(models.User).filter(models.User.tenant_id == tenant_id).all()

    @staticmethod
    def get_user(db: Session, tenant_id: int, user_id: int) -> models.User:
        """
        Tek bir kullanıcı detayını getirir.
        """
        return UserService._get_user_in_tenant_or_404(db, tenant_id, user_id)

    @staticmethod
    def create_user(
        db: Session,
        current_user: models.User,
        data: schemas.UserCreate,
    ) -> models.User:
        """
        Yeni bir kullanıcı oluşturur ve şifresini güvenli (bcrypt) şekilde hashler.
        """
        tenant_id = current_user.tenant_id

        # Şifre hashleme (app.core.security modülünden)
        password_hash = get_password_hash(data.password)

        user = models.User(
            tenant_id=tenant_id,
            email=data.email,
            password_hash=password_hash,
            full_name=data.full_name,
            role=data.role,
            is_active=data.is_active,
        )

        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists in this tenant.",
            )

        db.refresh(user)

        # Audit Log
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="user",
            entity_id=user.id,
            action="CREATE",
            changes={
                "email": data.email,
                "full_name": data.full_name,
                "role": data.role,
                "is_active": data.is_active,
            },
        )

        return user

    @staticmethod
    def update_user(
        db: Session,
        tenant_id: int,
        user_id: int,
        data: schemas.UserUpdate,
        current_user: models.User,
    ) -> models.User:
        """
        Kullanıcı bilgilerini günceller (Tam güncelleme).
        """
        user = UserService._get_user_in_tenant_or_404(db, tenant_id, user_id)

        before = user.__dict__.copy()

        user.full_name = data.full_name
        user.email = data.email
        user.role = data.role
        user.is_active = data.is_active

        # Eğer yeni şifre gönderildiyse hashleyerek güncelle
        if data.password:
            user.password_hash = get_password_hash(data.password)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists in this tenant.",
            )

        db.refresh(user)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="user",
            entity_id=user.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": data.model_dump(exclude={"password"}),
            },
        )

        return user

    @staticmethod
    def partial_update_user(
        db: Session,
        tenant_id: int,
        user_id: int,
        data: schemas.UserPartialUpdate,
        current_user: models.User,
    ) -> models.User:
        """
        Kullanıcı bilgilerini kısmi günceller.
        """
        user = UserService._get_user_in_tenant_or_404(db, tenant_id, user_id)
        update_data = data.model_dump(exclude_unset=True)

        before = user.__dict__.copy()

        for field, value in update_data.items():
            if field == "password" and value:
                user.password_hash = get_password_hash(value)
            else:
                setattr(user, field, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists in this tenant.",
            )

        db.refresh(user)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="user",
            entity_id=user.id,
            action="PATCH",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return user

    @staticmethod
    def delete_user(
        db: Session,
        tenant_id: int,
        user_id: int,
        current_user: models.User,
    ):
        """
        Kullanıcıyı siler. Kendini silmeye çalışırsa hata verir.
        """
        user = UserService._get_user_in_tenant_or_404(db, tenant_id, user_id)

        # Güvenlik: Kişinin kendini silmesini engelle
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account.",
            )

        before = user.__dict__.copy()

        db.delete(user)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="user",
            entity_id=user_id,
            action="DELETE",
            changes={"before": before},
        )