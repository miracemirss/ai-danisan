from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class SubscriptionStatus(str, Enum):
    TRIALING = "TRIALING"
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    # PostgreSQL'deki subscription_status enum değerleriyle birebir aynı olmalı


class SubscriptionBase(BaseModel):
    plan_id: int
    status: SubscriptionStatus | None = None  # None => DB default TRIALING
    starts_at: datetime
    trial_ends_at: datetime | None = None
    ends_at: datetime | None = None
    external_customer_id: str | None = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    plan_id: int | None = None
    status: SubscriptionStatus | None = None
    starts_at: datetime | None = None
    trial_ends_at: datetime | None = None
    ends_at: datetime | None = None
    external_customer_id: str | None = None


class SubscriptionOut(SubscriptionBase):
    id: int
    tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        # Pydantic v1:
        # orm_mode = True
