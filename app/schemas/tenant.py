# app/schemas/tenant.py

from datetime import datetime
from pydantic import BaseModel, field_validator


class TenantBase(BaseModel):
    name: str
    slug: str | None = None        # boş gelirse service'de name'den slug üretebiliriz
    country: str | None = None     # "TR", "US" vs.
    timezone: str | None = "Europe/Istanbul"
    is_active: bool | None = True

    @field_validator("country")
    @classmethod
    def validate_country(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError("country must be 2-letter ISO code, e.g. 'TR'")
        return v


class TenantCreate(TenantBase):
    # Şimdilik ekstra bir şey yok; istersek slug'ı zorunlu yapabiliriz
    pass


class TenantUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    country: str | None = None
    timezone: str | None = None
    is_active: bool | None = None


class TenantOut(TenantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # Pydantic v1 ise:
        # orm_mode = True
