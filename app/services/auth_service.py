# app/services/auth_service.py

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.database import get_db


# Swagger + dependency'ler için OAuth2 şeması
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _slugify(value: str) -> str:
    """
    Çok basit bir slugify implementasyonu.
    İstersen ileride 'python-slugify' paketine geçebiliriz.
    """
    return (
        value.strip()
        .lower()
        .replace(" ", "-")
        .replace("_", "-")
    )


def create_tenant_and_owner(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    İlk kayıt olan kullanıcı için:
    - Yeni bir tenant oluşturur
    - O tenant altında 'OWNER' rolünde user açar
    """
    tenant = models.Tenant(
        name=user_in.tenant_name,
        slug=_slugify(user_in.tenant_name),
        is_active=True,
    )
    db.add(tenant)
    db.flush()  # tenant.id oluşsun

    user = models.User(
        tenant_id=tenant.id,
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=get_password_hash(user_in.password),
        role="OWNER",  # enum tarafında OWNER olarak tanımlı
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    Email + şifre ile kullanıcı doğrular.
    Doğruysa User, yanlışsa None döner.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# =========================
#  JWT'den current user çekme
# =========================
# app/services/auth_service.py (DEBUG VERSİYONU)

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
) -> models.User:
    """
    DEBUG VERSİYONU: Hatanın sebebini terminale basar.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Token Çözülüyor mu?
        print(f"\n🔍 DEBUG: Token decode ediliyor... (Algoritma: {settings.JWT_ALGORITHM})")

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # 2. Payload İçeriği Ne?
        print(f"✅ DEBUG: Payload çözüldü: {payload}")

        user_id = payload.get("sub")

        if user_id is None:
            print("❌ DEBUG: Payload içinde 'sub' (user_id) alanı yok!")
            raise credentials_exception

        print(f"🔍 DEBUG: Aranacak User ID: {user_id} (Tipi: {type(user_id)})")

    except JWTError as e:
        # 🔥 EN ÖNEMLİ KISIM BURASI
        print(f"🔥🔥 DEBUG: JWT Hatası oluştu: {str(e)}")
        # Genelde "Signature verification failed" veya "Signature has expired" yazar.
        raise credentials_exception

    # 3. Veritabanında Kullanıcı Var mı?
    try:
        # int() çevriminde hata olup olmadığına da bakalım
        user_id_int = int(user_id)
        user = db.query(models.User).filter(models.User.id == user_id_int).first()
    except ValueError:
        print(f"❌ DEBUG: user_id integer'a çevrilemedi: {user_id}")
        raise credentials_exception

    if user is None:
        print(f"❌ DEBUG: User ID {user_id} veritabanında bulunamadı!")
        raise credentials_exception

    print(f"✅ DEBUG: Kullanıcı bulundu: {user.email}")
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Kullanıcının 'is_active' durumunu kontrol eder.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
