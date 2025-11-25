# app/routers/auth.py

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, models
from app.core.config import settings
from app.core.security import create_access_token
from app.database import get_db
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register(
        user_in: schemas.UserCreate,
        db: Session = Depends(get_db),
):
    """
    Sisteme yeni bir tenant (işletme) ve yönetici (owner) kaydeder.
    """
    existing_user = auth_service.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = auth_service.create_tenant_and_owner(db, user_in)
    return user


@router.post("/login", response_model=schemas.Token)
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    """
    Kullanıcı girişi yapar ve JWT Access Token döner.
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token süresini ayarlardan al
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    # Token oluştur (Payload içine gerekli bilgileri ekle)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": user.tenant_id,
            "role": user.role,
        },
        expires_delta=access_token_expires,
    )

    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=schemas.UserRead)
def read_users_me(
        current_user: models.User = Depends(auth_service.get_current_user)
):
    """
    Giriş yapmış olan kullanıcının kendi bilgilerini döner.
    """
    return current_user