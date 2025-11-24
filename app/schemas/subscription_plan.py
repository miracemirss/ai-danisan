from datetime import datetime
from pydantic import BaseModel, field_validator


class SubscriptionPlanBase(BaseModel):
    code: str
    name: str
    monthly_price: float
    currency: str = "TRY"
    max_practitioners: int | None = None
    max_clients: int | None = None

    @field_validator("monthly_price")
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("monthly_price must be >= 0")
        return v

    @field_validator("max_practitioners", "max_clients")
    @classmethod
    def validate_limits(cls, v):
        if v is not None and v < 0:
            raise ValueError("limits must be >= 0")
        return v


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    monthly_price: float | None = None
    currency: str | None = None
    max_practitioners: int | None = None
    max_clients: int | None = None

    @field_validator("monthly_price")
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("monthly_price must be >= 0")
        return v

    @field_validator("max_practitioners", "max_clients")
    @classmethod
    def validate_limits(cls, v):
        if v is not None and v < 0:
            raise ValueError("limits must be >= 0")
        return v


class SubscriptionPlanOut(SubscriptionPlanBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        # Pydantic v1 ise:
        # orm_mode = True
