# app/services/user_service.py

from typing import List

from sqlalchemy.orm import Session as SASession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app import models, schemas
from app.services.audit_log_service import AuditLogService
from app.core.security import get_password_hash  # ✅ BURASI ÖNEMLİ


class UserService:

    @staticmethod
    def _get_user_in_tenant_or_404(
        db: SASession,
        tenant_id: int,
        user_id: int,
    ) -> models.User:
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
    def create_user(
        db: SASession,
        current_user: models.User,
        data: schemas.UserCreate,
    ) -> models.User:
        tenant_id = current_user.tenant_id

        # ❌ hash_password değil
        # ✅ get_password_hash kullanıyoruz
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
        db: SASession,
        tenant_id: int,
        user_id: int,
        data: schemas.UserUpdate,
        current_user: models.User,
    ) -> models.User:
        user = UserService._get_user_in_tenant_or_404(db, tenant_id, user_id)

        before = user.__dict__.copy()

        user.full_name = data.full_name
        user.email = data.email
        user.role = data.role
        user.is_active = data.is_active

        if data.password:
            user.password_hash = get_password_hash(data.password)  # ✅

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
                "after": {
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                },
            },
        )

        return user

    @staticmethod
    def partial_update_user(
        db: SASession,
        tenant_id: int,
        user_id: int,
        data: schemas.UserPartialUpdate,
        current_user: models.User,
    ) -> models.User:
        user = UserService._get_user_in_tenant_or_404(db, tenant_id, user_id)
        update_data = data.model_dump(exclude_unset=True)

        before = user.__dict__.copy()

        if "full_name" in update_data:
            user.full_name = update_data["full_name"]

        if "role" in update_data:
            user.role = update_data["role"]

        if "is_active" in update_data:
            user.is_active = update_data["is_active"]

        if "password" in update_data and update_data["password"]:
            user.password_hash = get_password_hash(update_data["password"])  # ✅

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
