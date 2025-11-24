# app/routers/reports.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as SASession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.report_service import ReportService
from app import schemas, models

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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return ReportService.create_report(
        db=db,
        current_user=current_user,
        data=report_in,
    )


@router.get("/", response_model=list[schemas.ReportOut])
def list_reports(
    client_id: int | None = None,
    practitioner_id: int | None = None,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Filtreler:
    - client_id verilirse: sadece o danışanın raporları
    - practitioner_id verilirse: sadece o uzmanın raporları
    - ikisi birden verilirse: kesişim
    - hiçbiri verilmezse: tenant'taki tüm raporlar
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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return ReportService.get_report(
        db=db,
        tenant_id=current_user.tenant_id,
        report_id=report_id,
    )


@router.put("/{report_id}", response_model=schemas.ReportOut)
def update_report(
    report_id: int,
    report_in: schemas.ReportBase,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ReportService.delete_report(
        db=db,
        tenant_id=current_user.tenant_id,
        report_id=report_id,
        current_user=current_user,
    )
    return
