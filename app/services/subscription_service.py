from sqlalchemy.orm import Session as SASession
from fastapi import HTTPException, status

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class SubscriptionService:

    # --- iç yardımcılar ---

    @staticmethod
    def _ensure_plan_exists(db: SASession, plan_id: int):
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
        db: SASession,
        tenant_id: int,
        subscription_id: int,
    ):
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

    # --- CRUD metotları ---

    @staticmethod
    def create_subscription(
        db: SASession,
        current_user: models.User,
        data: schemas.SubscriptionCreate,
    ):
        tenant_id = current_user.tenant_id

        # plan var mı?
        SubscriptionService._ensure_plan_exists(db=db, plan_id=data.plan_id)

        # İstersen: aynı tenant için birden fazla ACTIVE/TRIALING subscription engelle
        # ...

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

        # 🔥 AUDIT LOG – CREATE
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription",
            entity_id=sub.id,
            action="create",
            changes=data.model_dump(),
        )

        return sub

    @staticmethod
    def list_subscriptions(
        db: SASession,
        tenant_id: int,
    ):
        return (
            db.query(models.Subscription)
            .filter(models.Subscription.tenant_id == tenant_id)
            .order_by(models.Subscription.starts_at.desc())
            .all()
        )

    @staticmethod
    def get_subscription(
        db: SASession,
        tenant_id: int,
        subscription_id: int,
    ):
        return SubscriptionService._get_subscription_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )

    @staticmethod
    def update_subscription(
        db: SASession,
        tenant_id: int,
        subscription_id: int,
        data: schemas.SubscriptionBase,
        current_user: models.User,
    ):
        sub = SubscriptionService._get_subscription_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )

        # plan değişiyorsa kontrol et
        SubscriptionService._ensure_plan_exists(db=db, plan_id=data.plan_id)

        before = sub.__dict__.copy()

        update_data = data.model_dump()
        for field, value in update_data.items():
            setattr(sub, field, value)

        db.commit()
        db.refresh(sub)

        # 🔥 AUDIT LOG – UPDATE
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription",
            entity_id=sub.id,
            action="update",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return sub

    @staticmethod
    def partial_update_subscription(
        db: SASession,
        tenant_id: int,
        subscription_id: int,
        data: schemas.SubscriptionUpdate,
        current_user: models.User,
    ):
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

        # 🔥 AUDIT LOG – PATCH
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription",
            entity_id=sub.id,
            action="patch",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return sub

    @staticmethod
    def delete_subscription(
        db: SASession,
        tenant_id: int,
        subscription_id: int,
        current_user: models.User,
    ):
        sub = SubscriptionService._get_subscription_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )
        before = sub.__dict__.copy()

        db.delete(sub)
        db.commit()

        # 🔥 AUDIT LOG – DELETE
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription",
            entity_id=subscription_id,
            action="delete",
            changes={"before": before},
        )

        return
