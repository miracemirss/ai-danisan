from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as SASession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.subscription_service import SubscriptionService
from app import schemas, models

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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SubscriptionService.create_subscription(
        db=db,
        current_user=current_user,   # 🔥 Audit log için gerekli
        data=subscription_in,
    )


@router.get("/", response_model=list[schemas.SubscriptionOut])
def list_subscriptions(
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SubscriptionService.list_subscriptions(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/{subscription_id}", response_model=schemas.SubscriptionOut)
def get_subscription(
    subscription_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SubscriptionService.get_subscription(
        db=db,
        tenant_id=current_user.tenant_id,
        subscription_id=subscription_id,
    )


@router.put("/{subscription_id}", response_model=schemas.SubscriptionOut)
def update_subscription(
    subscription_id: int,
    subscription_in: schemas.SubscriptionBase,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SubscriptionService.update_subscription(
        db=db,
        tenant_id=current_user.tenant_id,
        subscription_id=subscription_id,
        data=subscription_in,
        current_user=current_user,   # 🔥 Ekledik
    )


@router.patch("/{subscription_id}", response_model=schemas.SubscriptionOut)
def partial_update_subscription(
    subscription_id: int,
    subscription_in: schemas.SubscriptionUpdate,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SubscriptionService.partial_update_subscription(
        db=db,
        tenant_id=current_user.tenant_id,
        subscription_id=subscription_id,
        data=subscription_in,
        current_user=current_user,   # 🔥 Ekledik
    )


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    SubscriptionService.delete_subscription(
        db=db,
        tenant_id=current_user.tenant_id,
        subscription_id=subscription_id,
        current_user=current_user,   # 🔥 Ekledik
    )
    return
