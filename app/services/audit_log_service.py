# app/services/audit_log_service.py

from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models


class AuditLogService:
    """
    Audit Log (Denetim Kaydı) servisi.
    Sistemdeki kritik değişikliklerin (Create, Update, Delete) kaydını tutar.
    """

    @staticmethod
    def log(
        db: Session,
        user: Optional[models.User],
        entity: str,
        entity_id: int,
        action: str,
        changes: Optional[Dict[str, Any]] = None,
    ) -> models.AuditLog:
        """
        Yeni bir audit log kaydı oluşturur.
        Sistem tarafından otomatik çağrılır, API üzerinden manuel tetiklenmez.
        """

        log = models.AuditLog(
            tenant_id=user.tenant_id if user else None,
            user_id=user.id if user else None,
            entity_type=entity,
            entity_id=entity_id,
            action=action,
            changes=changes,
        )

        db.add(log)
        db.commit()
        # Log kaydı sadece insert edildiği için refresh genellikle gerekmez, 
        # ancak ID'ye hemen ihtiyaç varsa eklenebilir.
        return log

    @staticmethod
    def list_logs(db: Session, tenant_id: int) -> List[models.AuditLog]:
        """
        Bir tenant'a ait tüm audit loglarını, yeniden eskiye doğru listeler.
        """
        return (
            db.query(models.AuditLog)
            .filter(models.AuditLog.tenant_id == tenant_id)
            .order_by(models.AuditLog.created_at.desc())
            .all()
        )

    @staticmethod
    def get_log(db: Session, tenant_id: int, log_id: int) -> models.AuditLog:
        """
        Tek bir audit log kaydını getirir.
        """
        log = (
            db.query(models.AuditLog)
            .filter(
                models.AuditLog.id == log_id,
                models.AuditLog.tenant_id == tenant_id
            )
            .first()
        )
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found.",
            )
        return log