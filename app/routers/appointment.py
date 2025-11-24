# app/routers/appointments.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services import auth_service
from app.services import appointment_service

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)


@router.post(
    "",
    response_model=schemas.AppointmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    data: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user),
):
    """Yeni randevu oluştur (tenant + current_user context'inde)."""
    return appointment_service.create_appointment(
        db=db,
        current_user=current_user,
        data=data,
    )


@router.get(
    "",
    response_model=List[schemas.AppointmentOut],
)
def list_appointments(
    practitioner_id: Optional[int] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user),
):
    """Bu tenant için randevu listesini getir."""
    return appointment_service.list_appointments(
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
    current_user: models.User = Depends(auth_service.get_current_user),
):
    # İstersen burada 404 check’i servise de bırakabilirsin
    appt = appointment_service.get_appointment(
        db=db,
        tenant_id=current_user.tenant_id,
        appointment_id=appointment_id,
    )
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@router.put(
    "/{appointment_id}",
    response_model=schemas.AppointmentOut,
)
def update_appointment(
    appointment_id: int,
    data: schemas.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user),
):
    return appointment_service.update_appointment(
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
    current_user: models.User = Depends(auth_service.get_current_user),
):
    return appointment_service.change_status(
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
    current_user: models.User = Depends(auth_service.get_current_user),
):
    appointment_service.delete_appointment(
        db=db,
        tenant_id=current_user.tenant_id,
        appointment_id=appointment_id,
        current_user=current_user,
    )
    return None
