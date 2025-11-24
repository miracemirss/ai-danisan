# app/services/session_note_service.py

from sqlalchemy.orm import Session as SASession
from fastapi import HTTPException, status

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class SessionNoteService:

    # --- İç helper'lar ---

    @staticmethod
    def _ensure_session_in_tenant(
        db: SASession,
        tenant_id: int,
        session_id: int,
    ):
        session = (
            db.query(models.SessionModel)
            .filter(
                models.SessionModel.id == session_id,
                models.SessionModel.tenant_id == tenant_id,
            )
            .first()
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session not found for this tenant.",
            )

    @staticmethod
    def _ensure_author_in_tenant(
        db: SASession,
        tenant_id: int,
        author_id: int,
    ):
        user = (
            db.query(models.User)
            .filter(
                models.User.id == author_id,
                models.User.tenant_id == tenant_id,
            )
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Author (user) not found for this tenant.",
            )

    @staticmethod
    def _get_note_with_tenant_check(
        db: SASession,
        tenant_id: int,
        note_id: int,
    ):
        # session_notes'ta tenant yok → sessions'a join ile kontrol
        note = (
            db.query(models.SessionNoteModel)
            .join(
                models.SessionModel,
                models.SessionModel.id == models.SessionNoteModel.session_id,
            )
            .filter(
                models.SessionNoteModel.id == note_id,
                models.SessionModel.tenant_id == tenant_id,
            )
            .first()
        )
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session note not found.",
            )
        return note

    # --- CRUD metotları + AUDIT LOG ---

    @staticmethod
    def create_note(
        db: SASession,
        current_user: models.User,
        data: schemas.SessionNoteCreate,
    ):
        tenant_id = current_user.tenant_id

        # session mevcut mu ve tenant'a mı ait?
        SessionNoteService._ensure_session_in_tenant(
            db=db,
            tenant_id=tenant_id,
            session_id=data.session_id,
        )

        # author_id gelmemişse current_user.id kullan
        author_id = data.author_id or current_user.id

        # author aynı tenant'tan mı?
        SessionNoteService._ensure_author_in_tenant(
            db=db,
            tenant_id=tenant_id,
            author_id=author_id,
        )

        note = models.SessionNoteModel(
            session_id=data.session_id,
            author_id=author_id,
            type=data.type or schemas.NoteType.RAW,
            content=data.content,
            is_private=data.is_private if data.is_private is not None else True,
        )

        db.add(note)
        db.commit()
        db.refresh(note)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="session_note",
            entity_id=note.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return note

    @staticmethod
    def list_notes(
        db: SASession,
        tenant_id: int,
        session_id: int | None = None,
    ):
        q = (
            db.query(models.SessionNoteModel)
            .join(
                models.SessionModel,
                models.SessionModel.id == models.SessionNoteModel.session_id,
            )
            .filter(models.SessionModel.tenant_id == tenant_id)
        )

        if session_id is not None:
            q = q.filter(models.SessionNoteModel.session_id == session_id)

        return q.order_by(models.SessionNoteModel.created_at.desc()).all()

    @staticmethod
    def get_note(
        db: SASession,
        tenant_id: int,
        note_id: int,
    ):
        return SessionNoteService._get_note_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            note_id=note_id,
        )

    @staticmethod
    def update_note(
        db: SASession,
        tenant_id: int,
        note_id: int,
        data: schemas.SessionNoteBase,
        current_user: models.User,
    ):
        note = SessionNoteService._get_note_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            note_id=note_id,
        )

        # session / author değişiyorsa tenant kontrollerini tekrar yap
        new_session_id = data.session_id
        new_author_id = data.author_id or note.author_id

        if new_session_id is not None and new_session_id != note.session_id:
            SessionNoteService._ensure_session_in_tenant(
                db=db,
                tenant_id=tenant_id,
                session_id=new_session_id,
            )

        if new_author_id != note.author_id:
            SessionNoteService._ensure_author_in_tenant(
                db=db,
                tenant_id=tenant_id,
                author_id=new_author_id,
            )

        before = note.__dict__.copy()
        update_data = data.model_dump()

        for field, value in update_data.items():
            if field == "author_id" and value is None:
                value = new_author_id
            setattr(note, field, value)

        db.commit()
        db.refresh(note)


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="session_note",
            entity_id=note.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return note

    @staticmethod
    def partial_update_note(
        db: SASession,
        tenant_id: int,
        note_id: int,
        data: schemas.SessionNoteUpdate,
        current_user: models.User,
    ):
        note = SessionNoteService._get_note_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            note_id=note_id,
        )
        update_data = data.model_dump(exclude_unset=True)

        new_session_id = update_data.get("session_id", note.session_id)
        new_author_id = update_data.get("author_id", note.author_id)

        # tenant kontrolleri
        SessionNoteService._ensure_session_in_tenant(
            db=db,
            tenant_id=tenant_id,
            session_id=new_session_id,
        )
        SessionNoteService._ensure_author_in_tenant(
            db=db,
            tenant_id=tenant_id,
            author_id=new_author_id,
        )

        before = note.__dict__.copy()

        for field, value in update_data.items():
            setattr(note, field, value)

        db.commit()
        db.refresh(note)


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="session_note",
            entity_id=note.id,
            action="PATCH",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return note

    @staticmethod
    def delete_note(
        db: SASession,
        tenant_id: int,
        note_id: int,
        current_user: models.User,
    ):
        note = SessionNoteService._get_note_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            note_id=note_id,
        )
        before = note.__dict__.copy()

        db.delete(note)
        db.commit()


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="session_note",
            entity_id=note_id,
            action="DELETE",
            changes={"before": before},
        )

        return
