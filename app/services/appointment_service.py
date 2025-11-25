# app/services/appointment_service.py

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class AppointmentService:
    """
    Randevu (Appointment) işlemleri için servis katmanı.
    """

    @staticmethod
    def _get_appointment_or_404(
        db: Session,
        tenant_id: int,
        appointment_id: int,
    ) -> models.Appointment:
        """
        Yardımcı fonksiyon: ID'ye göre randevuyu arar, yoksa 404 hatası fırlatır.
        """
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

    @staticmethod
    def create_appointment(
        db: Session,
        current_user: models.User,
        data: schemas.AppointmentCreate,
    ) -> models.Appointment:
        """
        Yeni bir randevu oluşturur.
        Eğer 'practitioner_id' gönderilmezse, işlemi yapan kullanıcıyı (current_user) atar.
        """
        practitioner_id = data.practitioner_id or current_user.id

        appt = models.Appointment(
            tenant_id=current_user.tenant_id,
            practitioner_id=practitioner_id,
            client_id=data.client_id,
            starts_at=data.starts_at,
            ends_at=data.ends_at,
            status="SCHEDULED",  # Varsayılan statü
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

    @staticmethod
    def get_appointment(
        db: Session,
        tenant_id: int,
        appointment_id: int,
    ) -> models.Appointment:
        """
        Tek bir randevuyu getirir. Bulamazsa 404 verir.
        """
        return AppointmentService._get_appointment_or_404(db, tenant_id, appointment_id)

    @staticmethod
    def list_appointments(
        db: Session,
        tenant_id: int,
        practitioner_id: Optional[int] = None,
        client_id: Optional[int] = None,
    ) -> List[models.Appointment]:
        """
        Randevuları listeler. Practitioner veya Client bazlı filtreleme yapılabilir.
        """
        q = db.query(models.Appointment).filter(models.Appointment.tenant_id == tenant_id)

        if practitioner_id is not None:
            q = q.filter(models.Appointment.practitioner_id == practitioner_id)

        if client_id is not None:
            q = q.filter(models.Appointment.client_id == client_id)

        return q.order_by(models.Appointment.starts_at.desc()).all()

    @staticmethod
    def update_appointment(
        db: Session,
        tenant_id: int,
        appointment_id: int,
        data: schemas.AppointmentUpdate,
        current_user: models.User,
    ) -> models.Appointment:
        """
        Randevu detaylarını günceller.
        """
        appt = AppointmentService._get_appointment_or_404(db, tenant_id, appointment_id)

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

    @staticmethod
    def change_status(
        db: Session,
        tenant_id: int,
        appointment_id: int,
        status: schemas.AppointmentStatus,
        current_user: models.User,
    ) -> models.Appointment:
        """
        Sadece randevu statüsünü değiştirir (örn: COMPLETED, CANCELED).
        """
        appt = AppointmentService._get_appointment_or_404(db, tenant_id, appointment_id)

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

    @staticmethod
    def delete_appointment(
        db: Session,
        tenant_id: int,
        appointment_id: int,
        current_user: models.User,
    ) -> None:
        """
        Randevuyu siler.
        """
        appt = AppointmentService._get_appointment_or_404(db, tenant_id, appointment_id)
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