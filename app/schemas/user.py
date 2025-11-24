# app/schemas/user.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str  # "OWNER" | "PRACTITIONER" | "STAFF" | "ADMIN"
    is_active: bool = True


class UserCreate(UserBase):
    password: str  # plaintext gelecek, hash'ini service tarafında alacağız


class UserUpdate(UserBase):
    # Tam update (PUT) için
    password: Optional[str] = None  # istersen zorunlu da yapabilirsin


class UserPartialUpdate(BaseModel):
    # Patch için hepsi optional
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    id: int
    tenant_id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True  # Pydantic v1 kullanıyorsan bunu aç
