# app/routers/auth.py

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.core.security import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    decode_access_token,
)
from app import schemas, models
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# Bearer token yapısını kuruyoruz
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=schemas.UserRead, status_code=201)
def register(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    """
    İlk kullanıcı aynı zamanda tenant (işletme/klinik) sahibini oluşturur.
    """
    existing = auth_service.get_user_by_email(db, user_in.email)
    if existing:
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
    Kullanıcı girişi.
    OAuth2PasswordRequestForm → username + password (username = email)
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": user.tenant_id,
            "role": user.role,
        },
        expires_delta=access_token_expires,
    )

    return schemas.Token(access_token=access_token, token_type="bearer")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Header'daki Bearer token'dan kullanıcıyı çözer.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user)):
    """
    Mevcut oturum açmış kullanıcı bilgilerini döner.
    """
    return current_user
