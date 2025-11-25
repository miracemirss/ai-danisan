# app/schemas/user.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str = "STAFF"  # Varsayılan rol, register ekranında gönderilmezse STAFF olur
    is_active: bool = True


class UserCreate(UserBase):
    """
    Mevcut bir tenant içine kullanıcı eklerken (Admin panelinden) kullanılır.
    Sadece şifre ve kullanıcı bilgileri yeterlidir.
    """
    password: str


class UserRegister(UserCreate):
    """
    🔥 İLK KAYIT İÇİN GEREKLİ ŞEMA
    Sisteme ilk kez kayıt olan (Register) kullanıcılar için kullanılır.
    UserCreate'in tüm özelliklerini (email, password, vb.) taşır + tenant_name ekler.
    """
    tenant_name: str = Field(..., min_length=3, description="Oluşturulacak şirket/klinik adı")


class UserUpdate(UserBase):
    """
    Kullanıcıyı tamamen güncellemek (PUT) için kullanılır.
    """
    password: Optional[str] = None


class UserPartialUpdate(BaseModel):
    """
    Kullanıcıyı kısmi güncellemek (PATCH) için kullanılır.
    Tüm alanlar opsiyoneldir.
    """
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    """
    API yanıtlarında (Response) kullanıcıyı dönerken kullanılır.
    Şifreyi (password) asla içermez.
    """
    id: int
    tenant_id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 uyumlu (eski adıyla orm_mode=True)