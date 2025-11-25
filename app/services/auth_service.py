# app/services/auth_service.py

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app import models, schemas
from app.core import security
from app.core.config import settings
from app.core.utils import slugify
from app.database import get_db

# Token URL'si auth router'ındaki login endpoint'ini işaret eder
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_tenant_and_owner(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    İlk kayıt (Register) işlemi:
    - Yeni bir Tenant (İşletme) oluşturur.
    - Kullanıcıyı bu tenant'ın 'OWNER'ı olarak kaydeder.
    """
    # 1. Tenant Oluştur
    tenant = models.Tenant(
        name=user_in.tenant_name,
        slug=slugify(user_in.tenant_name),
        is_active=True,
    )
    db.add(tenant)
    db.flush()  # ID oluşması için flush (commit değil)

    # 2. Owner Kullanıcısını Oluştur
    hashed_password = security.get_password_hash(user_in.password)

    user = models.User(
        tenant_id=tenant.id,
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=hashed_password,
        role="OWNER",
        is_active=True,
    )
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise e

    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    Login işlemi: Email ve şifreyi doğrular.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not security.verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Email adresine göre kullanıcıyı getirir.
    """
    return db.query(models.User).filter(models.User.email == email).first()


# ==========================================
#  MERKEZİ AUTH DEPENDENCY (BAĞIMLILIK)
# ==========================================
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
) -> models.User:
    """
    Tüm korumalı endpoint'lerde kullanılan dependency.
    JWT Token'ı doğrular ve ilgili kullanıcıyı veritabanından çeker.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Token decode işlemi (Ayarlar config'den)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except (JWTError, ValidationError):
        raise credentials_exception

    # Kullanıcıyı bul
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id_int).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user