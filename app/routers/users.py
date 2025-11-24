# app/routers/users.py

from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session as SASession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.user_service import UserService
from app import schemas, models

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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Örnek rol kontrolü:
    # if current_user.role not in ("OWNER", "ADMIN"):
    #     raise HTTPException(status_code=403, detail="Not allowed to create users")

    return UserService.create_user(
        db=db,
        current_user=current_user,
        data=user_in,
    )


@router.get("/", response_model=List[schemas.UserOut])
def list_users(
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return UserService.list_users(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(
    user_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return UserService.get_user(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=user_id,
    )


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Burada hard delete yerine istersen soft delete yapabilirsin (is_active = False)
    UserService.delete_user(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=user_id,
        current_user=current_user,
    )
    return
