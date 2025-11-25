# app/routers/users.py

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Mevcut tenant altına yeni bir kullanıcı (personel/yönetici) oluşturur.
    Sadece yetkili kullanıcılar erişebilir.
    """
    # İleride buraya 'if current_user.role != "ADMIN"' gibi yetki kontrolleri eklenebilir.
    return UserService.create_user(
        db=db,
        current_user=current_user,
        data=user_in,
    )


@router.get("/", response_model=List[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Mevcut kullanıcının ait olduğu tenant'taki tüm kullanıcıları listeler.
    """
    return UserService.list_users(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Belirli bir kullanıcının detaylarını getirir.
    """
    return UserService.get_user(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=user_id,
    )


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Kullanıcı bilgilerini günceller (Tam güncelleme).
    """
    return UserService.update_user(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=user_id,
        data=user_in,
        current_user=current_user,
    )


@router.patch("/{user_id}", response_model=schemas.UserOut)
def partial_update_user(
    user_id: int,
    user_in: schemas.UserPartialUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Kullanıcı bilgilerini kısmi günceller (Örn: Sadece şifre veya rol).
    """
    return UserService.partial_update_user(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=user_id,
        data=user_in,
        current_user=current_user,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Kullanıcıyı siler.
    """
    UserService.delete_user(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=user_id,
        current_user=current_user,
    )
    return