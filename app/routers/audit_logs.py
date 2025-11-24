from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.audit_log_service import AuditLogService
from app import schemas, models


router = APIRouter(
    prefix="/audit-logs",
    tags=["audit_logs"],
)


@router.get("/", response_model=list[schemas.AuditLogOut])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AuditLogService.list_logs(
        db=db,
        tenant_id=current_user.tenant_id
    )


@router.get("/{log_id}", response_model=schemas.AuditLogOut)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AuditLogService.get_log(db, current_user.tenant_id, log_id)
