# app/services/ai_summary_service.py

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class AiSummaryService:
    """
    Yapay Zeka Özetleri (AI Summaries) için CRUD yönetim servisi.
    Seans notları veya transkriptler üzerinden oluşturulan özetleri yönetir.
    """

    @staticmethod
    def _ensure_session_in_tenant(
            db: Session,
            tenant_id: int,
            session_id: int,
    ) -> None:
        """
        Belirtilen seansın tenant'a ait olup olmadığını doğrular.
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
    def _get_summary_with_tenant_check(
            db: Session,
            tenant_id: int,
            summary_id: int,
    ) -> models.AiSummary:
        """
        ID'ye göre özeti getirir ve tenant kontrolü yapar.
        """
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

    @staticmethod
    def create_summary(
            db: Session,
            current_user: models.User,
            data: schemas.AiSummaryCreate,
    ) -> models.AiSummary:
        """
        Yeni bir AI özeti oluşturur.
        """
        tenant_id = current_user.tenant_id

        # Seans kontrolü
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

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ai_summary",
            entity_id=summary.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return summary

    @staticmethod
    def list_summaries(
            db: Session,
            tenant_id: int,
            session_id: Optional[int] = None,
    ) -> List[models.AiSummary]:
        """
        Tenant'a ait özetleri listeler.
        session_id verilirse sadece o seansa ait özetler döner.
        """
        q = db.query(models.AiSummary).filter(
            models.AiSummary.tenant_id == tenant_id
        )

        if session_id is not None:
            q = q.filter(models.AiSummary.session_id == session_id)

        return q.order_by(models.AiSummary.created_at.desc()).all()

    @staticmethod
    def get_summary(
            db: Session,
            tenant_id: int,
            summary_id: int,
    ) -> models.AiSummary:
        """
        Tek bir özeti detaylarıyla getirir.
        """
        return AiSummaryService._get_summary_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            summary_id=summary_id,
        )

    @staticmethod
    def update_summary(
            db: Session,
            tenant_id: int,
            summary_id: int,
            data: schemas.AiSummaryBase,
            current_user: models.User,
    ) -> models.AiSummary:
        """
        Özeti günceller (Tam güncelleme).
        Seans ID değişiyorsa tenant kontrolü yapılır.
        """
        summary = AiSummaryService._get_summary_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            summary_id=summary_id,
        )

        # Seans değişiyorsa kontrol et
        if data.session_id != summary.session_id:
            AiSummaryService._ensure_session_in_tenant(
                db=db,
                tenant_id=tenant_id,
                session_id=data.session_id,
            )

        before = summary.__dict__.copy()
        update_data = data.model_dump()

        for field, value in update_data.items():
            setattr(summary, field, value)

        db.commit()
        db.refresh(summary)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ai_summary",
            entity_id=summary.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return summary

    @staticmethod
    def partial_update_summary(
            db: Session,
            tenant_id: int,
            summary_id: int,
            data: schemas.AiSummaryUpdate,
            current_user: models.User,
    ) -> models.AiSummary:
        """
        Özeti kısmi günceller.
        """
        summary = AiSummaryService._get_summary_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            summary_id=summary_id,
        )

        update_data = data.model_dump(exclude_unset=True)

        # Seans değişiyorsa kontrol et
        if "session_id" in update_data:
            AiSummaryService._ensure_session_in_tenant(
                db=db,
                tenant_id=tenant_id,
                session_id=update_data["session_id"],
            )

        before = summary.__dict__.copy()

        for field, value in update_data.items():
            setattr(summary, field, value)

        db.commit()
        db.refresh(summary)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ai_summary",
            entity_id=summary.id,
            action="PATCH",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return summary

    @staticmethod
    def delete_summary(
            db: Session,
            tenant_id: int,
            summary_id: int,
            current_user: models.User,
    ) -> None:
        """
        Özeti siler.
        """
        summary = AiSummaryService._get_summary_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            summary_id=summary_id,
        )

        before = summary.__dict__.copy()

        db.delete(summary)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ai_summary",
            entity_id=summary_id,
            action="DELETE",
            changes={"before": before},
        )

        return