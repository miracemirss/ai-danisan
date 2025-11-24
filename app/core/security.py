# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
import hashlib
import secrets


# NOT: Prod ortamda .env'den okumamız lazım, şimdilik sabit dursun.
SECRET_KEY = "CHANGE_THIS_SECRET_KEY"  # sonra .env'e taşıyacağız
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 gün


# ========== PAROLA HASH / VERIFY ==========

def get_password_hash(password: str) -> str:
    """
    Basit ama güvenli bir SHA-256 + salt şifreleme.
    Format: salt$hash
    """
    # 16 byte’lık random salt
    salt = secrets.token_hex(16)  # 32 karakterlik hex string

    # salt + password -> sha256
    data = (salt + password).encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()

    # "salt$hash" şeklinde saklıyoruz
    return f"{salt}${digest}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kullanıcının girdiği şifreyi, DB'deki salt+hash ile doğrular.
    """
    try:
        salt, expected_digest = hashed_password.split("$", 1)
    except ValueError:
        # Beklenen formatta değilse zaten geçersiz
        return False

    data = (salt + plain_password).encode("utf-8")
    actual_digest = hashlib.sha256(data).hexdigest()

    return secrets.compare_digest(actual_digest, expected_digest)


# ========== JWT TOKEN OLUŞTURMA / ÇÖZME ==========

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Kullanıcı bilgilerini içeren JWT token üretir.
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    JWT token'ı decode eder. Hatalıysa JWTError fırlatır.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise
