# app/routers/clients.py

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.client_service import ClientService

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)


@router.post(
    "/",
    response_model=schemas.ClientOut,
    status_code=status.HTTP_201_CREATED
)
def create_client(
    client_in: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir danışan (client) oluşturur.
    """
    return ClientService.create_client(
        db=db,
        tenant_id=current_user.tenant_id,
        data=client_in,
        current_user=current_user,
    )


@router.get("/", response_model=List[schemas.ClientOut])
def list_clients(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Mevcut tenant'a ait tüm danışanları listeler.
    """
    return ClientService.list_clients(
        db=db,
        tenant_id=current_user.tenant_id
    )


@router.get("/{client_id}", response_model=schemas.ClientOut)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Belirli bir danışanın detaylarını getirir.
    """
    return ClientService.get_client(
        db=db,
        tenant_id=current_user.tenant_id,
        client_id=client_id
    )


@router.put("/{client_id}", response_model=schemas.ClientOut)
def update_client(
    client_id: int,
    client_in: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Danışan bilgilerini günceller (Tam güncelleme).
    """
    return ClientService.update_client(
        db=db,
        tenant_id=current_user.tenant_id,
        client_id=client_id,
        data=client_in,
        current_user=current_user,
    )


@router.patch("/{client_id}", response_model=schemas.ClientOut)
def partial_update_client(
    client_id: int,
    client_in: schemas.ClientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Danışan bilgilerini kısmi günceller.
    """
    return ClientService.partial_update_client(
        db=db,
        tenant_id=current_user.tenant_id,
        client_id=client_id,
        data=client_in,
        current_user=current_user,
    )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Bir danışanı siler.
    """
    ClientService.delete_client(
        db=db,
        tenant_id=current_user.tenant_id,
        client_id=client_id,
        current_user=current_user,
    )
    return