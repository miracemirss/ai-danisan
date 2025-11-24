# app/schemas/auth.py

from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    tenant_id: int
    role: str


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """
    Kayıt olurken kullanılacak body.
    Aynı anda tenant da oluşturacağımız için tenant_name ekliyoruz.
    """
    password: str
    tenant_name: str


class UserLogin(BaseModel):
    """
    İstersen ileride JSON body ile login yapmak için.
    Şu an /auth/login form-data ile çalışıyor (OAuth2PasswordRequestForm).
    """
    email: EmailStr
    password: str


class UserRead(UserBase):
    """
    Kullanıcıyı dışarı dönerken kullanılacak schema.
    Şifre hiçbir zaman buradan dönmüyor.
    """
    id: int
    tenant_id: int
    role: str

    class Config:
        from_attributes = True  # SQLAlchemy modeli → Pydantic modele dönüşüm için
