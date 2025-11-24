from sqlalchemy.orm import Session
from app import models


class AuditLogService:

    @staticmethod
    def log(
        db: Session,
        user: models.User | None,
        entity: str,
        entity_id: int,
        action: str,
        changes: dict | None = None,
    ):
        """
        Sistem tarafından otomatik çağrılır. Kullanıcı çağırmaz.
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
        # refresh gerekmez — audit log sadece kayıt için
        return log

    @staticmethod
    def list_logs(db: Session, tenant_id: int):
        """
        Sadece okuma yetkilidir.
        """
        return (
            db.query(models.AuditLog)
            .filter(models.AuditLog.tenant_id == tenant_id)
            .order_by(models.AuditLog.created_at.desc())
            .all()
        )

    @staticmethod
    def get_log(db: Session, tenant_id: int, log_id: int):
        log = (
            db.query(models.AuditLog)
            .filter(
                models.AuditLog.id == log_id,
                models.AuditLog.tenant_id == tenant_id
            )
            .first()
        )
        if not log:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found.",
            )
        return log
