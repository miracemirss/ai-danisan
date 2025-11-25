# app/routers/subscription_plans.py

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.subscription_plan_service import SubscriptionPlanService

router = APIRouter(
    prefix="/subscription-plans",
    tags=["subscription_plans"],
)


@router.post(
    "/",
    response_model=schemas.SubscriptionPlanOut,
    status_code=status.HTTP_201_CREATED,
)
def create_subscription_plan(
    plan_in: schemas.SubscriptionPlanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir abonelik planı oluşturur.
    Genellikle sistem yöneticileri tarafından kullanılır.
    """
    return SubscriptionPlanService.create_plan(
        db=db,
        data=plan_in,
        current_user=current_user,
    )


@router.get("/", response_model=List[schemas.SubscriptionPlanOut])
def list_subscription_plans(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Sistemdeki tüm abonelik planlarını listeler.
    """
    return SubscriptionPlanService.list_plans(db=db)


@router.get("/{plan_id}", response_model=schemas.SubscriptionPlanOut)
def get_subscription_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir abonelik planının detaylarını getirir.
    """
    return SubscriptionPlanService.get_plan(
        db=db,
        plan_id=plan_id,
    )


@router.put("/{plan_id}", response_model=schemas.SubscriptionPlanOut)
def update_subscription_plan(
    plan_id: int,
    plan_in: schemas.SubscriptionPlanBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Abonelik planını günceller (Tam güncelleme).
    """
    return SubscriptionPlanService.update_plan(
        db=db,
        plan_id=plan_id,
        data=plan_in,
        current_user=current_user,
    )


@router.patch("/{plan_id}", response_model=schemas.SubscriptionPlanOut)
def partial_update_subscription_plan(
    plan_id: int,
    plan_in: schemas.SubscriptionPlanUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Abonelik planını kısmi olarak günceller.
    """
    return SubscriptionPlanService.partial_update_plan(
        db=db,
        plan_id=plan_id,
        data=plan_in,
        current_user=current_user,
    )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Bir abonelik planını siler.
    """
    SubscriptionPlanService.delete_plan(
        db=db,
        plan_id=plan_id,
        current_user=current_user,
    )
    return