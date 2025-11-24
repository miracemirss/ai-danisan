# app/schemas/client.py
from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from enum import Enum


class ClientStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
    # PostgreSQL'deki client_status ile birebir aynı olmalı


class ClientBase(BaseModel):
    first_name: str
    last_name: str
    gender: str | None = None
    date_of_birth: date | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    notes: str | None = None
    status: ClientStatus | None = None  # create'de boş gelirse DB default kullanılır
    primary_practitioner_id: int | None = None


class ClientCreate(ClientBase):
    # İstersen burada bazı alanları zorunlu bırakıp Base'ten override edebilirsin
    pass


class ClientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    notes: str | None = None
    status: ClientStatus | None = None
    primary_practitioner_id: int | None = None


class ClientOut(ClientBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True        # Eğer Pydantic v1 kullanıyorsan bunu kullan
