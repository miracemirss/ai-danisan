# app/services/session_note_service.py

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class SessionNoteService:
    """
    Seans Notları (Session Notes) için CRUD yönetim servisi.
    Notların belirli bir seansa ve yazara (User) ait olmasını ve
    tenant sınırları içinde kalmasını sağlar.
    """

    @staticmethod
    def _ensure_session_in_tenant(
        db: Session,
        tenant_id: int,
        session_id: int,
    ) -> None:
        """
        Belirtilen seansın, belirtilen tenant'a ait olup olmadığını doğrular.
        """
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
        db: Session,
        tenant_id: int,
        author_id: int,
    ) -> None:
        """
        Notu yazan kullanıcının (author), belirtilen tenant'a ait olup olmadığını doğrular.
        """
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
        db: Session,
        tenant_id: int,
        note_id: int,
    ) -> models.SessionNoteModel:
        """
        ID'ye göre notu getirir. Not tablosunda tenant_id olmadığı için
        ilişkili Session üzerinden tenant kontrolü yapar.
        """
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

    @staticmethod
    def create_note(
        db: Session,
        current_user: models.User,
        data: schemas.SessionNoteCreate,
    ) -> models.SessionNoteModel:
        """
        Yeni bir seans notu oluşturur.
        """
        tenant_id = current_user.tenant_id

        # Seans kontrolü
        SessionNoteService._ensure_session_in_tenant(
            db=db,
            tenant_id=tenant_id,
            session_id=data.session_id,
        )

        # Yazar (Author) kontrolü: Gönderilmemişse current_user atanır
        author_id = data.author_id or current_user.id
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
        db: Session,
        tenant_id: int,
        session_id: Optional[int] = None,
    ) -> List[models.SessionNoteModel]:
        """
        Tenant'a ait seans notlarını listeler.
        session_id verilirse sadece o seansa ait notları döner.
        """
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
        db: Session,
        tenant_id: int,
        note_id: int,
    ) -> models.SessionNoteModel:
        """
        Tek bir notun detayını getirir.
        """
        return SessionNoteService._get_note_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            note_id=note_id,
        )

    @staticmethod
    def update_note(
        db: Session,
        tenant_id: int,
        note_id: int,
        data: schemas.SessionNoteBase,
        current_user: models.User,
    ) -> models.SessionNoteModel:
        """
        Notu günceller (Tam güncelleme - PUT).
        Eğer seans veya yazar değiştiriliyorsa tenant kontrolü tekrarlanır.
        """
        note = SessionNoteService._get_note_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            note_id=note_id,
        )

        # Yeni değerleri al
        new_session_id = data.session_id
        new_author_id = data.author_id or note.author_id

        # Seans değişiyorsa kontrol et
        if new_session_id is not None and new_session_id != note.session_id:
            SessionNoteService._ensure_session_in_tenant(
                db=db,
                tenant_id=tenant_id,
                session_id=new_session_id,
            )

        # Yazar değişiyorsa kontrol et
        if new_author_id != note.author_id:
            SessionNoteService._ensure_author_in_tenant(
                db=db,
                tenant_id=tenant_id,
                author_id=new_author_id,
            )

        before = note.__dict__.copy()
        update_data = data.model_dump()

        for field, value in update_data.items():
            # Eğer author_id None geldiyse (model_dump kaynaklı), mevcut değeri koru veya yeni değeri ata
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
        db: Session,
        tenant_id: int,
        note_id: int,
        data: schemas.SessionNoteUpdate,
        current_user: models.User,
    ) -> models.SessionNoteModel:
        """
        Notu kısmi günceller (PATCH).
        """
        note = SessionNoteService._get_note_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            note_id=note_id,
        )
        update_data = data.model_dump(exclude_unset=True)

        new_session_id = update_data.get("session_id", note.session_id)
        new_author_id = update_data.get("author_id", note.author_id)

        # Tenant kontrolleri
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
        db: Session,
        tenant_id: int,
        note_id: int,
        current_user: models.User,
    ) -> None:
        """
        Notu siler.
        """
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