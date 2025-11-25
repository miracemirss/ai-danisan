# app/routers/practitioners.py

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.practitioner_service import PractitionerService

router = APIRouter(
    prefix="/practitioners",
    tags=["practitioners"],
)


@router.post(
    "/",
    response_model=schemas.PractitionerProfileOut,
    status_code=status.HTTP_201_CREATED,
)
def create_practitioner_profile(
    profile_in: schemas.PractitionerProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir uygulayıcı (doktor/terapist vb.) profili oluşturur.
    Genellikle bir kullanıcı (User) ile ilişkilidir.
    """
    return PractitionerService.create_profile(
        db=db,
        current_user=current_user,
        data=profile_in,
    )


@router.get("/", response_model=List[schemas.PractitionerProfileOut])
def list_practitioners(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Mevcut tenant'a ait tüm uygulayıcı profillerini listeler.
    """
    return PractitionerService.list_profiles(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/{profile_id}", response_model=schemas.PractitionerProfileOut)
def get_practitioner_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir uygulayıcı profilinin detaylarını getirir.
    """
    return PractitionerService.get_profile(
        db=db,
        tenant_id=current_user.tenant_id,
        profile_id=profile_id,
    )


@router.put("/{profile_id}", response_model=schemas.PractitionerProfileOut)
def update_practitioner_profile(
    profile_id: int,
    profile_in: schemas.PractitionerProfileBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Uygulayıcı profilini günceller (Tam güncelleme).
    """
    return PractitionerService.update_profile(
        db=db,
        tenant_id=current_user.tenant_id,
        profile_id=profile_id,
        data=profile_in,
        current_user=current_user,
    )


@router.patch("/{profile_id}", response_model=schemas.PractitionerProfileOut)
def partial_update_practitioner_profile(
    profile_id: int,
    profile_in: schemas.PractitionerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Uygulayıcı profilini kısmi günceller.
    """
    return PractitionerService.partial_update_profile(
        db=db,
        tenant_id=current_user.tenant_id,
        profile_id=profile_id,
        data=profile_in,
        current_user=current_user,
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_practitioner_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Bir uygulayıcı profilini siler.
    """
    PractitionerService.delete_profile(
        db=db,
        tenant_id=current_user.tenant_id,
        profile_id=profile_id,
        current_user=current_user,
    )
    return