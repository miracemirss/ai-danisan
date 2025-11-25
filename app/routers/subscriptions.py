# app/routers/subscriptions.py

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.subscription_service import SubscriptionService

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)


@router.post(
    "/",
    response_model=schemas.SubscriptionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_subscription(
    subscription_in: schemas.SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir abonelik (subscription) oluşturur.
    """
    return SubscriptionService.create_subscription(
        db=db,
        current_user=current_user,
        data=subscription_in,
    )


@router.get("/", response_model=List[schemas.SubscriptionOut])
def list_subscriptions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Tenant'a ait tüm abonelikleri listeler.
    """
    return SubscriptionService.list_subscriptions(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/{subscription_id}", response_model=schemas.SubscriptionOut)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir abonelik detayını getirir.
    """
    return SubscriptionService.get_subscription(
        db=db,
        tenant_id=current_user.tenant_id,
        subscription_id=subscription_id,
    )


@router.put("/{subscription_id}", response_model=schemas.SubscriptionOut)
def update_subscription(
    subscription_id: int,
    subscription_in: schemas.SubscriptionBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Abonelik bilgilerini günceller (Tam güncelleme).
    """
    return SubscriptionService.update_subscription(
        db=db,
        tenant_id=current_user.tenant_id,
        subscription_id=subscription_id,
        data=subscription_in,
        current_user=current_user,
    )


@router.patch("/{subscription_id}", response_model=schemas.SubscriptionOut)
def partial_update_subscription(
    subscription_id: int,
    subscription_in: schemas.SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Abonelik bilgilerini kısmi olarak günceller.
    """
    return SubscriptionService.partial_update_subscription(
        db=db,
        tenant_id=current_user.tenant_id,
        subscription_id=subscription_id,
        data=subscription_in,
        current_user=current_user,
    )


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Bir aboneliği siler.
    """
    SubscriptionService.delete_subscription(
        db=db,
        tenant_id=current_user.tenant_id,
        subscription_id=subscription_id,
        current_user=current_user,
    )
    return