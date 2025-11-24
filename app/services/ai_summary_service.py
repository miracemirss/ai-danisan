from sqlalchemy.orm import Session as SASession
from fastapi import HTTPException, status

from app import models, schemas


class AiSummaryService:

    # --- helpers ---

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
    def _get_summary_with_tenant_check(
        db: SASession,
        tenant_id: int,
        summary_id: int,
    ):
        summary = (
            db.query(models.AiSummary)
            .filter(
                models.AiSummary.id == summary_id,
                models.AiSummary.tenant_id == tenant_id,
            )
            .first()
        )
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI summary not found.",
            )
        return summary

    # --- CRUD ---

    @staticmethod
    def create_summary(
        db: SASession,
        current_user: models.User,
        data: schemas.AiSummaryCreate,
    ):
        tenant_id = current_user.tenant_id

        AiSummaryService._ensure_session_in_tenant(
            db=db,
            tenant_id=tenant_id,
            session_id=data.session_id,
        )

        summary = models.AiSummary(
            tenant_id=tenant_id,
            session_id=data.session_id,
            source_note_id=data.source_note_id,
            job_id=data.job_id,
            summary_text=data.summary_text,
            key_points=data.key_points,
            risk_flags=data.risk_flags,
        )

        db.add(summary)
        db.commit()
        db.refresh(summary)
        return summary

    @staticmethod
    def list_summaries(
        db: SASession,
        tenant_id: int,
        session_id: int | None = None,
    ):
        q = db.query(models.AiSummary).filter(
            models.AiSummary.tenant_id == tenant_id
        )

        if session_id is not None:
            q = q.filter(models.AiSummary.session_id == session_id)

        return q.order_by(models.AiSummary.created_at.desc()).all()

    @staticmethod
    def get_summary(
        db: SASession,
        tenant_id: int,
        summary_id: int,
    ):
        return AiSummaryService._get_summary_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            summary_id=summary_id,
        )

    @staticmethod
    def update_summary(
        db: SASession,
        tenant_id: int,
        summary_id: int,
        data: schemas.AiSummaryBase,
    ):
        summary = AiSummaryService._get_summary_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            summary_id=summary_id,
        )

        AiSummaryService._ensure_session_in_tenant(
            db=db,
            tenant_id=tenant_id,
            session_id=data.session_id,
        )

        for field, value in data.model_dump().items():
            setattr(summary, field, value)

        db.commit()
        db.refresh(summary)
        return summary

    @staticmethod
    def partial_update_summary(
        db: SASession,
        tenant_id: int,
        summary_id: int,
        data: schemas.AiSummaryUpdate,
    ):
        summary = AiSummaryService._get_summary_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            summary_id=summary_id,
        )

        update_data = data.model_dump(exclude_unset=True)

        if "session_id" in update_data:
            AiSummaryService._ensure_session_in_tenant(
                db=db,
                tenant_id=tenant_id,
                session_id=update_data["session_id"],
            )

        for field, value in update_data.items():
            setattr(summary, field, value)

        db.commit()
        db.refresh(summary)
        return summary

    @staticmethod
    def delete_summary(
        db: SASession,
        tenant_id: int,
        summary_id: int,
    ):
        summary = AiSummaryService._get_summary_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            summary_id=summary_id,
        )
        db.delete(summary)
        db.commit()
        return
