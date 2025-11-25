# app/services/subscription_plan_service.py

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class SubscriptionPlanService:
    """
    Abonelik Planları (Subscription Plans) için CRUD yönetim servisi.
    Genellikle sadece Admin yetkisiyle yönetilir.
    """

    @staticmethod
    def _get_plan_or_404(db: Session, plan_id: int) -> models.SubscriptionPlan:
        """
        Yardımcı fonksiyon: ID'ye göre planı arar, bulamazsa 404 hatası fırlatır.
        """
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

    @staticmethod
    def create_plan(
        db: Session,
        data: schemas.SubscriptionPlanCreate,
        current_user: models.User,
    ) -> models.SubscriptionPlan:
        """
        Yeni bir abonelik planı oluşturur.
        """
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription plan with this code already exists.",
            )

        db.refresh(plan)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription_plan",
            entity_id=plan.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return plan

    @staticmethod
    def list_plans(db: Session) -> List[models.SubscriptionPlan]:
        """
        Tüm abonelik planlarını fiyata göre artan sırada listeler.
        """
        return (
            db.query(models.SubscriptionPlan)
            .order_by(models.SubscriptionPlan.monthly_price.asc())
            .all()
        )

    @staticmethod
    def get_plan(db: Session, plan_id: int) -> models.SubscriptionPlan:
        """
        ID ile tek bir plan detayını getirir.
        """
        return SubscriptionPlanService._get_plan_or_404(db, plan_id)

    @staticmethod
    def update_plan(
        db: Session,
        plan_id: int,
        data: schemas.SubscriptionPlanBase,
        current_user: models.User,
    ) -> models.SubscriptionPlan:
        """
        Abonelik planını günceller (Tam güncelleme - PUT).
        """
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription plan code already exists.",
            )

        db.refresh(plan)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription_plan",
            entity_id=plan.id,
            action="UPDATE",
            changes={"before": before, "after": update_data},
        )

        return plan

    @staticmethod
    def partial_update_plan(
        db: Session,
        plan_id: int,
        data: schemas.SubscriptionPlanUpdate,
        current_user: models.User,
    ) -> models.SubscriptionPlan:
        """
        Abonelik planını kısmi olarak günceller (PATCH).
        """
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription plan code already exists.",
            )

        db.refresh(plan)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription_plan",
            entity_id=plan.id,
            action="PATCH",
            changes={"before": before, "after": update_data},
        )

        return plan

    @staticmethod
    def delete_plan(
        db: Session,
        plan_id: int,
        current_user: models.User,
    ) -> None:
        """
        Abonelik planını siler.
        Dikkat: Bu plana bağlı aktif abonelikler varsa veritabanı kısıtlaması nedeniyle hata alabilirsiniz.
        """
        plan = SubscriptionPlanService._get_plan_or_404(db, plan_id)
        before = plan.__dict__.copy()

        db.delete(plan)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="subscription_plan",
            entity_id=plan_id,
            action="DELETE",
            changes={"before": before},
        )