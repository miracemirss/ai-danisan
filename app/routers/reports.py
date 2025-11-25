# app/routers/reports.py

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.report_service import ReportService

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.post(
    "/",
    response_model=schemas.ReportOut,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
        report_in: schemas.ReportCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir rapor oluşturur.
    """
    return ReportService.create_report(
        db=db,
        current_user=current_user,
        data=report_in,
    )


@router.get("/", response_model=List[schemas.ReportOut])
def list_reports(
        client_id: Optional[int] = None,
        practitioner_id: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Raporları listeler.

    Filtreler:
    - **client_id**: Sadece belirli bir danışana ait raporları getirir.
    - **practitioner_id**: Sadece belirli bir uzmana ait raporları getirir.
    - Hiçbiri verilmezse, tenant altındaki tüm raporları getirir.
    """
    return ReportService.list_reports(
        db=db,
        tenant_id=current_user.tenant_id,
        client_id=client_id,
        practitioner_id=practitioner_id,
    )


@router.get("/{report_id}", response_model=schemas.ReportOut)
def get_report(
        report_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir raporun detaylarını getirir.
    """
    return ReportService.get_report(
        db=db,
        tenant_id=current_user.tenant_id,
        report_id=report_id,
    )


@router.put("/{report_id}", response_model=schemas.ReportOut)
def update_report(
        report_id: int,
        report_in: schemas.ReportBase,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Rapor bilgilerini günceller (Tam güncelleme).
    """
    return ReportService.update_report(
        db=db,
        tenant_id=current_user.tenant_id,
        report_id=report_id,
        data=report_in,
        current_user=current_user,
    )


@router.patch("/{report_id}", response_model=schemas.ReportOut)
def partial_update_report(
        report_id: int,
        report_in: schemas.ReportUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Rapor bilgilerini kısmi olarak günceller.
    """
    return ReportService.partial_update_report(
        db=db,
        tenant_id=current_user.tenant_id,
        report_id=report_id,
        data=report_in,
        current_user=current_user,
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
        report_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Bir raporu siler.
    """
    ReportService.delete_report(
        db=db,
        tenant_id=current_user.tenant_id,
        report_id=report_id,
        current_user=current_user,
    )
    return