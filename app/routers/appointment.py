# app/routers/appointments.py

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.appointment_service import AppointmentService

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)


@router.post(
    "/",
    response_model=schemas.AppointmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    data: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir randevu oluşturur.
    """
    return AppointmentService.create_appointment(
        db=db,
        current_user=current_user,
        data=data,
    )


@router.get(
    "/",
    response_model=List[schemas.AppointmentOut],
)
def list_appointments(
    practitioner_id: Optional[int] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Tenant'a ait randevuları listeler.
    İsteğe bağlı olarak 'practitioner_id' veya 'client_id' ile filtreleme yapılabilir.
    """
    return AppointmentService.list_appointments(
        db=db,
        tenant_id=current_user.tenant_id,
        practitioner_id=practitioner_id,
        client_id=client_id,
    )


@router.get(
    "/{appointment_id}",
    response_model=schemas.AppointmentOut,
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir randevunun detaylarını getirir.
    """
    return AppointmentService.get_appointment(
        db=db,
        tenant_id=current_user.tenant_id,
        appointment_id=appointment_id,
    )


@router.put(
    "/{appointment_id}",
    response_model=schemas.AppointmentOut,
)
def update_appointment(
    appointment_id: int,
    data: schemas.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Randevu bilgilerini günceller (Tarih, notlar vb.).
    """
    return AppointmentService.update_appointment(
        db=db,
        tenant_id=current_user.tenant_id,
        appointment_id=appointment_id,
        data=data,
        current_user=current_user,
    )


@router.patch(
    "/{appointment_id}/status",
    response_model=schemas.AppointmentOut,
)
def update_appointment_status(
    appointment_id: int,
    status_value: schemas.AppointmentStatus,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Randevunun durumunu (örn: COMPLETED, CANCELED) günceller.
    """
    return AppointmentService.change_status(
        db=db,
        tenant_id=current_user.tenant_id,
        appointment_id=appointment_id,
        status=status_value,
        current_user=current_user,
    )


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Bir randevuyu siler.
    """
    AppointmentService.delete_appointment(
        db=db,
        tenant_id=current_user.tenant_id,
        appointment_id=appointment_id,
        current_user=current_user,
    )
    return