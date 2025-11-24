# app/services/appointment_service.py

from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app import models, schemas
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentStatus
from app.services.audit_log_service import AuditLogService


def _get_appointment_or_404(
    db: Session,
    *,
    tenant_id: int,
    appointment_id: int,
) -> models.Appointment:
    appt = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.id == appointment_id,
            models.Appointment.tenant_id == tenant_id,
        )
        .first()
    )
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return appt


def create_appointment(
    db: Session,
    *,
    current_user: models.User,
    data: schemas.AppointmentCreate,
) -> models.Appointment:
    """Yeni randevu oluşturur."""
    practitioner_id = data.practitioner_id or current_user.id

    appt = models.Appointment(
        tenant_id=current_user.tenant_id,
        practitioner_id=practitioner_id,
        client_id=data.client_id,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
        status="SCHEDULED",  # istersen schemas.AppointmentStatus.SCHEDULED.value kullan
        mode=data.mode,
        location_text=data.location_text,
        video_link=data.video_link,
        notes=data.notes,
    )

    db.add(appt)
    db.commit()
    db.refresh(appt)


    AuditLogService.log(
        db=db,
        user=current_user,
        entity="appointment",
        entity_id=appt.id,
        action="CREATE",
        changes=data.model_dump(),
    )

    return appt


def get_appointment(
    db: Session,
    *,
    tenant_id: int,
    appointment_id: int,
) -> Optional[models.Appointment]:
    # GET endpoint'inde Optional dönmek istiyorsan bunu kullanmaya devam edebilirsin
    return (
        db.query(models.Appointment)
        .filter(
            models.Appointment.id == appointment_id,
            models.Appointment.tenant_id == tenant_id,
        )
        .first()
    )


def list_appointments(
    db: Session,
    *,
    tenant_id: int,
    practitioner_id: Optional[int] = None,
    client_id: Optional[int] = None,
) -> List[models.Appointment]:
    q = db.query(models.Appointment).filter(models.Appointment.tenant_id == tenant_id)

    if practitioner_id is not None:
        q = q.filter(models.Appointment.practitioner_id == practitioner_id)

    if client_id is not None:
        q = q.filter(models.Appointment.client_id == client_id)

    return q.order_by(models.Appointment.starts_at.desc()).all()


def update_appointment(
    db: Session,
    *,
    tenant_id: int,
    appointment_id: int,
    data: AppointmentUpdate,
    current_user: models.User,
) -> models.Appointment:
    """Randevunun detaylarını günceller."""
    appt = _get_appointment_or_404(
        db=db,
        tenant_id=tenant_id,
        appointment_id=appointment_id,
    )

    before = appt.__dict__.copy()
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(appt, field, value)

    db.commit()
    db.refresh(appt)


    AuditLogService.log(
        db=db,
        user=current_user,
        entity="appointment",
        entity_id=appt.id,
        action="UPDATE",
        changes={
            "before": before,
            "after": update_data,
        },
    )

    return appt


def change_status(
    db: Session,
    *,
    tenant_id: int,
    appointment_id: int,
    status: AppointmentStatus,
    current_user: models.User,
) -> models.Appointment:
    appt = _get_appointment_or_404(
        db=db,
        tenant_id=tenant_id,
        appointment_id=appointment_id,
    )

    before_status = appt.status
    appt.status = status

    db.commit()
    db.refresh(appt)


    AuditLogService.log(
        db=db,
        user=current_user,
        entity="appointment",
        entity_id=appt.id,
        action="STATUS_CHANGE",
        changes={
            "before": before_status,
            "after": appt.status,
        },
    )

    return appt


def delete_appointment(
    db: Session,
    *,
    tenant_id: int,
    appointment_id: int,
    current_user: models.User,
) -> None:
    appt = _get_appointment_or_404(
        db=db,
        tenant_id=tenant_id,
        appointment_id=appointment_id,
    )
    before = appt.__dict__.copy()

    db.delete(appt)
    db.commit()


    AuditLogService.log(
        db=db,
        user=current_user,
        entity="appointment",
        entity_id=appointment_id,
        action="DELETE",
        changes={"before": before},
    )
