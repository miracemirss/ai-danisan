from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as SASession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.subscription_plan_service import SubscriptionPlanService
from app import schemas, models

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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Eğer sadece OWNER/ADMIN plan oluşturabilsin istersen burada role check ekleyebilirsin.
    return SubscriptionPlanService.create_plan(
        db=db,
        data=plan_in,
        current_user=current_user,  # 🔥 audit log için
    )


@router.get("/", response_model=list[schemas.SubscriptionPlanOut])
def list_subscription_plans(
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SubscriptionPlanService.list_plans(db=db)


@router.get("/{plan_id}", response_model=schemas.SubscriptionPlanOut)
def get_subscription_plan(
    plan_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SubscriptionPlanService.get_plan(
        db=db,
        plan_id=plan_id,
    )


@router.put("/{plan_id}", response_model=schemas.SubscriptionPlanOut)
def update_subscription_plan(
    plan_id: int,
    plan_in: schemas.SubscriptionPlanBase,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SubscriptionPlanService.update_plan(
        db=db,
        plan_id=plan_id,
        data=plan_in,
        current_user=current_user,  # 🔥 audit log için
    )


@router.patch("/{plan_id}", response_model=schemas.SubscriptionPlanOut)
def partial_update_subscription_plan(
    plan_id: int,
    plan_in: schemas.SubscriptionPlanUpdate,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SubscriptionPlanService.partial_update_plan(
        db=db,
        plan_id=plan_id,
        data=plan_in,
        current_user=current_user,  # 🔥 audit log için
    )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription_plan(
    plan_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    SubscriptionPlanService.delete_plan(
        db=db,
        plan_id=plan_id,
        current_user=current_user,  # 🔥 audit log için
    )
    return
