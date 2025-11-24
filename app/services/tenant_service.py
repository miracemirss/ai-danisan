# app/services/tenant_service.py

from sqlalchemy.orm import Session as SASession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app import models, schemas
from app.services.auth_service import _slugify  # daha önce yazmıştık
from app.services.audit_log_service import AuditLogService


class TenantService:

    # --- helpers ---

    @staticmethod
    def _get_tenant_or_404(db: SASession, tenant_id: int):
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

    # --- CRUD ---

    @staticmethod
    def create_tenant(
        db: SASession,
        data: schemas.TenantCreate,
        current_user: models.User | None = None,
    ):
        # Eğer sadece SUPER_ADMIN tenant oluşturabilsin istiyorsan burada kontrol edersin:
        # if current_user and current_user.role != models.UserRole.ADMIN:
        #     raise HTTPException(status_code=403, detail="Not allowed to create tenants")

        slug = data.slug or _slugify(data.name)

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
            user=current_user,  # bootstrap senaryosunda None olabilir
            entity="tenant",
            entity_id=tenant.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return tenant

    @staticmethod
    def list_tenants(db: SASession):
        # Bu endpoint'i sadece sistem admini kullanacaksa router'da role check yaparsın
        return (
            db.query(models.Tenant)
            .order_by(models.Tenant.created_at.desc())
            .all()
        )

    @staticmethod
    def get_tenant(db: SASession, tenant_id: int):
        return TenantService._get_tenant_or_404(db, tenant_id)

    @staticmethod
    def update_tenant(
        db: SASession,
        tenant_id: int,
        data: schemas.TenantBase,
        current_user: models.User,
    ):
        tenant = TenantService._get_tenant_or_404(db, tenant_id)

        before = tenant.__dict__.copy()

        slug = data.slug or tenant.slug or _slugify(data.name)

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
        db: SASession,
        tenant_id: int,
        data: schemas.TenantUpdate,
        current_user: models.User,
    ):
        tenant = TenantService._get_tenant_or_404(db, tenant_id)
        update_data = data.model_dump(exclude_unset=True)

        before = tenant.__dict__.copy()

        if "name" in update_data and "slug" not in update_data:
            # name değişti ama slug verilmedi → slug'ı istersen otomatik güncelle
            update_data["slug"] = _slugify(update_data["name"])

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
        db: SASession,
        tenant_id: int,
        current_user: models.User,
    ):
        tenant = TenantService._get_tenant_or_404(db, tenant_id)
        before = tenant.__dict__.copy()

        db.delete(tenant)
        db.commit()

        # 🔥 AUDIT LOG – DELETE
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="tenant",
            entity_id=tenant_id,
            action="DELETE",
            changes={"before": before},
        )

        return

    @staticmethod
    def get_current_user_tenant(
        db: SASession,
        current_user: models.User,
    ):
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
