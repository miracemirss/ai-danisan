# app/services/subscription_plan_service.py

from sqlalchemy.orm import Session as SASession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class SubscriptionPlanService:

    # -------------------------
    # Internal helper
    # -------------------------
    @staticmethod
    def _get_plan_or_404(db: SASession, plan_id: int):
        plan = (
            db.query(models.SubscriptionPlan)
            .filter(models.SubscriptionPlan.id == plan_id)
            .first()
        )
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found.",
            )
        return plan

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    def create_plan(
        db: SASession,
        data: schemas.SubscriptionPlanCreate,
        current_user: models.User,
    ):
        plan = models.SubscriptionPlan(
            code=data.code,
            name=data.name,
            monthly_price=data.monthly_price,
            currency=data.currency,
            max_practitioners=data.max_practitioners,
            max_clients=data.max_clients,
        )

        db.add(plan)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Subscription plan with this code already exists.",
            )

        db.refresh(plan)

        # 🔥 AUDIT LOG — CREATE
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription_plan",
            entity_id=plan.id,
            action="create",
            changes=data.model_dump(),
        )

        return plan

    # -------------------------
    # LIST
    # -------------------------
    @staticmethod
    def list_plans(db: SASession):
        return (
            db.query(models.SubscriptionPlan)
            .order_by(models.SubscriptionPlan.monthly_price.asc())
            .all()
        )

    # -------------------------
    # GET
    # -------------------------
    @staticmethod
    def get_plan(db: SASession, plan_id: int):
        return SubscriptionPlanService._get_plan_or_404(db, plan_id)

    # -------------------------
    # UPDATE (PUT)
    # -------------------------
    @staticmethod
    def update_plan(
        db: SASession,
        plan_id: int,
        data: schemas.SubscriptionPlanBase,
        current_user: models.User,
    ):
        plan = SubscriptionPlanService._get_plan_or_404(db, plan_id)

        before = plan.__dict__.copy()
        update_data = data.model_dump()

        for field, value in update_data.items():
            setattr(plan, field, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Subscription plan code already exists.",
            )

        db.refresh(plan)

        # 🔥 AUDIT LOG — UPDATE
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription_plan",
            entity_id=plan.id,
            action="update",
            changes={"before": before, "after": update_data},
        )

        return plan

    # -------------------------
    # PARTIAL UPDATE (PATCH)
    # -------------------------
    @staticmethod
    def partial_update_plan(
        db: SASession,
        plan_id: int,
        data: schemas.SubscriptionPlanUpdate,
        current_user: models.User,
    ):
        plan = SubscriptionPlanService._get_plan_or_404(db, plan_id)
        before = plan.__dict__.copy()

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(plan, field, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Subscription plan code already exists.",
            )

        db.refresh(plan)

        # 🔥 AUDIT LOG — PATCH
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription_plan",
            entity_id=plan.id,
            action="patch",
            changes={"before": before, "after": update_data},
        )

        return plan

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    def delete_plan(
        db: SASession,
        plan_id: int,
        current_user: models.User,
    ):
        plan = SubscriptionPlanService._get_plan_or_404(db, plan_id)
        before = plan.__dict__.copy()

        db.delete(plan)
        db.commit()

        # 🔥 AUDIT LOG — DELETE
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription_plan",
            entity_id=plan_id,
            action="delete",
            changes={"before": before},
        )

        return
