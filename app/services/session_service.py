# app/services/session_service.py

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession
# Çakışmayı önlemek için sqlalchemy Session'a alias verdik

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class SessionService:
    """
    Seans (Session) yönetim servisi.
    """

    @staticmethod
    def _ensure_practitioner_and_client_in_tenant(
        db: DbSession,
        tenant_id: int,
        practitioner_id: int,
        client_id: int,
    ):
        practitioner = (
            db.query(models.User)
            .filter(
                models.User.id == practitioner_id,
                models.User.tenant_id == tenant_id,
            )
            .first()
        )
        if not practitioner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Practitioner not found for this tenant.",
            )

        client = (
            db.query(models.Client)
            .filter(
                models.Client.id == client_id,
                models.Client.tenant_id == tenant_id,
            )
            .first()
        )
        if not client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client not found for this tenant.",
            )

    @staticmethod
    def _ensure_appointment_in_tenant_if_provided(
        db: DbSession,
        tenant_id: int,
        appointment_id: Optional[int],
    ):
        if appointment_id is None:
            return

        appointment = (
            db.query(models.Appointment)
            .filter(
                models.Appointment.id == appointment_id,
                models.Appointment.tenant_id == tenant_id,
            )
            .first()
        )
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment not found for this tenant.",
            )

    @staticmethod
    def create_session(
        db: DbSession,
        current_user: models.User,
        data: schemas.SessionCreate,
    ) -> models.Session:  # ✅ Düzeltildi: SessionModel -> Session
        tenant_id = current_user.tenant_id
        practitioner_id = data.practitioner_id or current_user.id
        client_id = data.client_id

        SessionService._ensure_practitioner_and_client_in_tenant(
            db=db,
            tenant_id=tenant_id,
            practitioner_id=practitioner_id,
            client_id=client_id,
        )
        SessionService._ensure_appointment_in_tenant_if_provided(
            db=db,
            tenant_id=tenant_id,
            appointment_id=data.appointment_id,
        )

        # ✅ Düzeltildi: models.SessionModel -> models.Session
        session = models.Session(
            tenant_id=tenant_id,
            practitioner_id=practitioner_id,
            client_id=client_id,
            appointment_id=data.appointment_id,
            session_type=data.session_type or schemas.SessionType.THERAPY,
            occurred_at=data.occurred_at,
            duration_min=data.duration_min,
            mood_score=data.mood_score,
            is_first_session=data.is_first_session or False,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="session",
            entity_id=session.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return session

    @staticmethod
    def list_sessions(
        db: DbSession,
        tenant_id: int,
    ) -> List[models.Session]: # ✅ Düzeltildi
        return (
            db.query(models.Session) # ✅ Düzeltildi
            .filter(models.Session.tenant_id == tenant_id)
            .order_by(models.Session.occurred_at.desc())
            .all()
        )

    @staticmethod
    def get_session(
        db: DbSession,
        tenant_id: int,
        session_id: int,
    ) -> models.Session: # ✅ Düzeltildi
        session = (
            db.query(models.Session) # ✅ Düzeltildi
            .filter(
                models.Session.id == session_id,
                models.Session.tenant_id == tenant_id,
            )
            .first()
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found.",
            )
        return session

    @staticmethod
    def update_session(
        db: DbSession,
        tenant_id: int,
        session_id: int,
        data: schemas.SessionBase,
        current_user: models.User,
    ) -> models.Session: # ✅ Düzeltildi
        session = SessionService.get_session(db, tenant_id, session_id)

        SessionService._ensure_practitioner_and_client_in_tenant(
            db=db,
            tenant_id=tenant_id,
            practitioner_id=data.practitioner_id,
            client_id=data.client_id,
        )
        SessionService._ensure_appointment_in_tenant_if_provided(
            db=db,
            tenant_id=tenant_id,
            appointment_id=data.appointment_id,
        )

        before = session.__dict__.copy()
        update_data = data.model_dump()

        for field, value in update_data.items():
            setattr(session, field, value)

        db.commit()
        db.refresh(session)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="session",
            entity_id=session.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return session

    @staticmethod
    def partial_update_session(
        db: DbSession,
        tenant_id: int,
        session_id: int,
        data: schemas.SessionUpdate,
        current_user: models.User,
    ) -> models.Session: # ✅ Düzeltildi
        session = SessionService.get_session(db, tenant_id, session_id)
        update_data = data.model_dump(exclude_unset=True)

        practitioner_id = update_data.get("practitioner_id", session.practitioner_id)
        client_id = update_data.get("client_id", session.client_id)
        appointment_id = update_data.get("appointment_id", session.appointment_id)

        SessionService._ensure_practitioner_and_client_in_tenant(
            db=db,
            tenant_id=tenant_id,
            practitioner_id=practitioner_id,
            client_id=client_id,
        )
        SessionService._ensure_appointment_in_tenant_if_provided(
            db=db,
            tenant_id=tenant_id,
            appointment_id=appointment_id,
        )

        before = session.__dict__.copy()

        for field, value in update_data.items():
            setattr(session, field, value)

        db.commit()
        db.refresh(session)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="session",
            entity_id=session.id,
            action="PATCH",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return session

    @staticmethod
    def delete_session(
        db: DbSession,
        tenant_id: int,
        session_id: int,
        current_user: models.User,
    ) -> None:
        session = SessionService.get_session(db, tenant_id, session_id)
        before = session.__dict__.copy()

        db.delete(session)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="session",
            entity_id=session_id,
            action="DELETE",
            changes={"before": before},
        )