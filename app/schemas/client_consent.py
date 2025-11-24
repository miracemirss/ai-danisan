from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class ConsentType(str, Enum):
    PRIVACY = "PRIVACY"
    TREATMENT = "TREATMENT"
    KVKK = "KVKK"
    # PostgreSQL enum değerleri burada olmalı


class ClientConsentBase(BaseModel):
    client_id: int
    type: ConsentType
    given_at: datetime
    revoked_at: datetime | None = None
    document_url: str | None = None


class ClientConsentCreate(ClientConsentBase):
    pass


class ClientConsentUpdate(BaseModel):
    revoked_at: datetime | None = None
    document_url: str | None = None


class ClientConsentOut(ClientConsentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
