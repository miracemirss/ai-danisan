# app/routers/audit_logs.py

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.audit_log_service import AuditLogService
from app.services.auth_service import get_current_user

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit_logs"],
)


@router.get("/", response_model=List[schemas.AuditLogOut])
def list_audit_logs(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Tenant'a ait tüm denetim (audit) kayıtlarını listeler.
    Genellikle sadece yöneticiler (Admin/Owner) tarafından görüntülenmelidir.
    """
    # İsteğe bağlı rol kontrolü buraya eklenebilir:
    # if current_user.role not in ["OWNER", "ADMIN"]: ...

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
    """
    Belirli bir denetim kaydının detaylarını getirir.
    """
    return AuditLogService.get_log(
        db=db,
        tenant_id=current_user.tenant_id,
        log_id=log_id,
    )