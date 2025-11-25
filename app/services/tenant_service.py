# app/services/tenant_service.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app import models, schemas
from app.core.utils import slugify
from app.services.audit_log_service import AuditLogService


class TenantService:
    """
    Tenant (İşletme/Klinik) CRUD işlemlerini yöneten servis sınıfı.
    """

    @staticmethod
    def _get_tenant_or_404(db: Session, tenant_id: int) -> models.Tenant:
        """
        Yardımcı fonksiyon: ID'ye göre tenant arar, bulamazsa 404 fırlatır.
        """
        tenant = (
            db.query(models.Tenant)
            .filter(models.Tenant.id == tenant_id)
            .first()
        )
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found.",
            )
        return tenant

    @staticmethod
    def create_tenant(
        db: Session,
        data: schemas.TenantCreate,
        current_user: Optional[models.User] = None,
    ) -> models.Tenant:
        """
        Yeni bir tenant oluşturur.
        """
        slug = data.slug or slugify(data.name)

        tenant = models.Tenant(
            name=data.name,
            slug=slug,
            country=data.country,
            timezone=data.timezone or "Europe/Istanbul",
            is_active=data.is_active if data.is_active is not None else True,
        )

        db.add(tenant)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant with this slug already exists.",
            )

        db.refresh(tenant)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="tenant",
            entity_id=tenant.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return tenant

    @staticmethod
    def list_tenants(db: Session) -> List[models.Tenant]:
        """
        Sistemdeki tüm tenant'ları listeler (En yeniden eskiye).
        """
        return (
            db.query(models.Tenant)
            .order_by(models.Tenant.created_at.desc())
            .all()
        )

    @staticmethod
    def get_tenant(db: Session, tenant_id: int) -> models.Tenant:
        """
        ID ile tenant detayını döner.
        """
        return TenantService._get_tenant_or_404(db, tenant_id)

    @staticmethod
    def update_tenant(
        db: Session,
        tenant_id: int,
        data: schemas.TenantBase,
        current_user: models.User,
    ) -> models.Tenant:
        """
        Tenant bilgilerini günceller (Tam güncelleme).
        """
        tenant = TenantService._get_tenant_or_404(db, tenant_id)

        before = tenant.__dict__.copy()

        slug = data.slug or tenant.slug or slugify(data.name)

        tenant.name = data.name
        tenant.slug = slug
        tenant.country = data.country
        tenant.timezone = data.timezone or tenant.timezone
        tenant.is_active = (
            data.is_active if data.is_active is not None else tenant.is_active
        )

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant with this slug already exists.",
            )

        db.refresh(tenant)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="tenant",
            entity_id=tenant.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": data.model_dump(),
            },
        )

        return tenant

    @staticmethod
    def partial_update_tenant(
        db: Session,
        tenant_id: int,
        data: schemas.TenantUpdate,
        current_user: models.User,
    ) -> models.Tenant:
        """
        Tenant bilgilerini kısmi günceller (Örn: Sadece isim).
        """
        tenant = TenantService._get_tenant_or_404(db, tenant_id)
        update_data = data.model_dump(exclude_unset=True)

        before = tenant.__dict__.copy()

        # İsim değiştiyse ve slug manuel verilmediyse, slug'ı güncelle
        if "name" in update_data and "slug" not in update_data:
            update_data["slug"] = slugify(update_data["name"])

        for field, value in update_data.items():
            setattr(tenant, field, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant with this slug already exists.",
            )

        db.refresh(tenant)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="tenant",
            entity_id=tenant.id,
            action="PATCH",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return tenant

    @staticmethod
    def delete_tenant(
        db: Session,
        tenant_id: int,
        current_user: models.User,
    ):
        """
        Tenant'ı siler.
        """
        tenant = TenantService._get_tenant_or_404(db, tenant_id)
        before = tenant.__dict__.copy()

        db.delete(tenant)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="tenant",
            entity_id=tenant.id,
            action="DELETE",
            changes={"before": before},
        )

    @staticmethod
    def get_current_user_tenant(
        db: Session,
        current_user: models.User,
    ) -> models.Tenant:
        """
        Kullanıcının bağlı olduğu tenant'ı döner.
        """
        tenant = (
            db.query(models.Tenant)
            .filter(models.Tenant.id == current_user.tenant_id)
            .first()
        )
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found for current user.",
            )
        return tenant