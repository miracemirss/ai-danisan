# app/routers/client_consents.py

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.client_consent_service import ClientConsentService

router = APIRouter(
    prefix="/client-consents",
    tags=["client_consents"]
)


@router.post("/", response_model=schemas.ClientConsentOut, status_code=status.HTTP_201_CREATED)
def create_consent(
    consent_in: schemas.ClientConsentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir danışan onayı (consent) formu oluşturur.
    """
    return ClientConsentService.create_consent(
        db=db,
        current_user=current_user,
        data=consent_in,
    )


@router.get("/", response_model=List[schemas.ClientConsentOut])
def list_consents(
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Onay formlarını listeler.
    İsteğe bağlı olarak **client_id** ile filtreleme yapılabilir.
    """
    return ClientConsentService.list_consents(
        db=db,
        tenant_id=current_user.tenant_id,
        client_id=client_id,
    )


@router.get("/{consent_id}", response_model=schemas.ClientConsentOut)
def get_consent(
    consent_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir onay formunun detaylarını getirir.
    """
    return ClientConsentService.get_consent(
        db=db,
        tenant_id=current_user.tenant_id,
        consent_id=consent_id,
    )


@router.patch("/{consent_id}", response_model=schemas.ClientConsentOut)
def update_consent(
    consent_id: int,
    consent_in: schemas.ClientConsentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Onay formunu günceller (Kısmi güncelleme).
    """
    return ClientConsentService.update_consent(
        db=db,
        tenant_id=current_user.tenant_id,
        consent_id=consent_id,
        data=consent_in,
        current_user=current_user,
    )


@router.delete("/{consent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consent(
    consent_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Bir onay formunu siler.
    """
    ClientConsentService.delete_consent(
        db=db,
        tenant_id=current_user.tenant_id,
        consent_id=consent_id,
        current_user=current_user,
    )
    return