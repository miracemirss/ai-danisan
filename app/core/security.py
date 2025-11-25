# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Union

import bcrypt
from jose import jwt

from app.core.config import settings

ALGORITHM = settings.JWT_ALGORITHM


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    JWT Access Token oluşturur.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Şifreyi doğrular (Bcrypt kullanarak).
    """
    # Bcrypt byte formatında çalışır, bu yüzden encode ediyoruz.
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """
    Şifreyi hashler (Bcrypt kullanarak).
    """
    # Rastgele salt ile hashle ve string olarak dön
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')