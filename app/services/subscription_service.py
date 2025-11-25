# app/services/subscription_service.py

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class SubscriptionService:
    """
    Abonelik (Subscription) işlemlerini yöneten servis sınıfı.
    """

    @staticmethod
    def _ensure_plan_exists(db: Session, plan_id: int) -> None:
        """
        Belirtilen abonelik planının var olup olmadığını kontrol eder.
        Yoksa 400 hatası fırlatır.
        """
        plan = (
            db.query(models.SubscriptionPlan)
            .filter(models.SubscriptionPlan.id == plan_id)
            .first()
        )
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription plan not found.",
            )

    @staticmethod
    def _get_subscription_with_tenant_check(
        db: Session,
        tenant_id: int,
        subscription_id: int,
    ) -> models.Subscription:
        """
        ID'ye göre aboneliği getirir ve tenant kontrolü yapar.
        """
        sub = (
            db.query(models.Subscription)
            .filter(
                models.Subscription.id == subscription_id,
                models.Subscription.tenant_id == tenant_id,
            )
            .first()
        )
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found.",
            )
        return sub

    @staticmethod
    def create_subscription(
        db: Session,
        current_user: models.User,
        data: schemas.SubscriptionCreate,
    ) -> models.Subscription:
        """
        Yeni bir abonelik oluşturur.
        """
        tenant_id = current_user.tenant_id

        # Plan kontrolü
        SubscriptionService._ensure_plan_exists(db=db, plan_id=data.plan_id)

        # İstenirse burada "Zaten aktif aboneliği var mı?" kontrolü eklenebilir.

        sub = models.Subscription(
            tenant_id=tenant_id,
            plan_id=data.plan_id,
            status=data.status or schemas.SubscriptionStatus.TRIALING,
            starts_at=data.starts_at,
            trial_ends_at=data.trial_ends_at,
            ends_at=data.ends_at,
            external_customer_id=data.external_customer_id,
        )

        db.add(sub)
        db.commit()
        db.refresh(sub)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription",
            entity_id=sub.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return sub

    @staticmethod
    def list_subscriptions(
        db: Session,
        tenant_id: int,
    ) -> List[models.Subscription]:
        """
        Tenant'a ait tüm abonelik geçmişini listeler.
        """
        return (
            db.query(models.Subscription)
            .filter(models.Subscription.tenant_id == tenant_id)
            .order_by(models.Subscription.starts_at.desc())
            .all()
        )

    @staticmethod
    def get_subscription(
        db: Session,
        tenant_id: int,
        subscription_id: int,
    ) -> models.Subscription:
        """
        Tek bir abonelik detayını getirir.
        """
        return SubscriptionService._get_subscription_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )

    @staticmethod
    def update_subscription(
        db: Session,
        tenant_id: int,
        subscription_id: int,
        data: schemas.SubscriptionBase,
        current_user: models.User,
    ) -> models.Subscription:
        """
        Abonelik bilgilerini günceller (Tam güncelleme).
        Plan ID değişiyorsa, yeni planın varlığı kontrol edilir.
        """
        sub = SubscriptionService._get_subscription_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )

        # Plan değişiyorsa kontrol et
        if data.plan_id != sub.plan_id:
            SubscriptionService._ensure_plan_exists(db=db, plan_id=data.plan_id)

        before = sub.__dict__.copy()
        update_data = data.model_dump()

        for field, value in update_data.items():
            setattr(sub, field, value)

        db.commit()
        db.refresh(sub)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription",
            entity_id=sub.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return sub

    @staticmethod
    def partial_update_subscription(
        db: Session,
        tenant_id: int,
        subscription_id: int,
        data: schemas.SubscriptionUpdate,
        current_user: models.User,
    ) -> models.Subscription:
        """
        Abonelik bilgilerini kısmi günceller.
        """
        sub = SubscriptionService._get_subscription_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )
        update_data = data.model_dump(exclude_unset=True)

        before = sub.__dict__.copy()

        if "plan_id" in update_data:
            SubscriptionService._ensure_plan_exists(
                db=db, plan_id=update_data["plan_id"]
            )

        for field, value in update_data.items():
            setattr(sub, field, value)

        db.commit()
        db.refresh(sub)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription",
            entity_id=sub.id,
            action="PATCH",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return sub

    @staticmethod
    def delete_subscription(
        db: Session,
        tenant_id: int,
        subscription_id: int,
        current_user: models.User,
    ) -> None:
        """
        Aboneliği siler.
        """
        sub = SubscriptionService._get_subscription_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )
        before = sub.__dict__.copy()

        db.delete(sub)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription",
            entity_id=subscription_id,
            action="DELETE",
            changes={"before": before},
        )