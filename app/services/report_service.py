# app/services/report_service.py

from sqlalchemy.orm import Session as SASession
from fastapi import HTTPException, status

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class ReportService:

    # --- İç yardımcılar ---

    @staticmethod
    def _ensure_client_in_tenant(
        db: SASession,
        tenant_id: int,
        client_id: int,
    ):
        client = (
            db.query(models.Client)
            .filter(
                models.Client.id == client_id,
                models.Client.tenant_id == tenant_id,
            )
            .first()
        )
        if not client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client not found for this tenant.",
            )

    @staticmethod
    def _ensure_practitioner_in_tenant(
        db: SASession,
        tenant_id: int,
        practitioner_id: int,
    ):
        practitioner = (
            db.query(models.User)
            .filter(
                models.User.id == practitioner_id,
                models.User.tenant_id == tenant_id,
            )
            .first()
        )
        if not practitioner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Practitioner not found for this tenant.",
            )

    @staticmethod
    def _get_report_with_tenant_check(
        db: SASession,
        tenant_id: int,
        report_id: int,
    ):
        report = (
            db.query(models.Report)
            .filter(
                models.Report.id == report_id,
                models.Report.tenant_id == tenant_id,
            )
            .first()
        )
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found.",
            )
        return report

    # --- CRUD metotları + AUDIT LOG ---

    @staticmethod
    def create_report(
        db: SASession,
        current_user: models.User,
        data: schemas.ReportCreate,
    ):
        tenant_id = current_user.tenant_id

        # client + practitioner aynı tenant'ta mı?
        ReportService._ensure_client_in_tenant(
            db=db,
            tenant_id=tenant_id,
            client_id=data.client_id,
        )
        ReportService._ensure_practitioner_in_tenant(
            db=db,
            tenant_id=tenant_id,
            practitioner_id=data.practitioner_id,
        )

        report = models.Report(
            tenant_id=tenant_id,
            client_id=data.client_id,
            practitioner_id=data.practitioner_id,
            period_start=data.period_start,
            period_end=data.period_end,
            title=data.title,
            content=data.content,
            pdf_url=data.pdf_url,
        )

        db.add(report)
        db.commit()
        db.refresh(report)


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="report",
            entity_id=report.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return report

    @staticmethod
    def list_reports(
        db: SASession,
        tenant_id: int,
        client_id: int | None = None,
        practitioner_id: int | None = None,
    ):
        q = db.query(models.Report).filter(models.Report.tenant_id == tenant_id)

        if client_id is not None:
            q = q.filter(models.Report.client_id == client_id)

        if practitioner_id is not None:
            q = q.filter(models.Report.practitioner_id == practitioner_id)

        return q.order_by(models.Report.created_at.desc()).all()

    @staticmethod
    def get_report(
        db: SASession,
        tenant_id: int,
        report_id: int,
    ):
        return ReportService._get_report_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            report_id=report_id,
        )

    @staticmethod
    def update_report(
        db: SASession,
        tenant_id: int,
        report_id: int,
        data: schemas.ReportBase,
        current_user: models.User,
    ):
        report = ReportService._get_report_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            report_id=report_id,
        )

        # tenant kontrolleri
        ReportService._ensure_client_in_tenant(
            db=db,
            tenant_id=tenant_id,
            client_id=data.client_id,
        )
        ReportService._ensure_practitioner_in_tenant(
            db=db,
            tenant_id=tenant_id,
            practitioner_id=data.practitioner_id,
        )

        before = report.__dict__.copy()
        update_data = data.model_dump()

        for field, value in update_data.items():
            setattr(report, field, value)

        db.commit()
        db.refresh(report)


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="report",
            entity_id=report.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return report

    @staticmethod
    def partial_update_report(
        db: SASession,
        tenant_id: int,
        report_id: int,
        data: schemas.ReportUpdate,
        current_user: models.User,
    ):
        report = ReportService._get_report_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            report_id=report_id,
        )
        update_data = data.model_dump(exclude_unset=True)

        # Eğer client/practitioner değişecekse tenant kontrolü yap
        new_client_id = update_data.get("client_id", report.client_id)
        new_practitioner_id = update_data.get(
            "practitioner_id", report.practitioner_id
        )

        ReportService._ensure_client_in_tenant(
            db=db,
            tenant_id=tenant_id,
            client_id=new_client_id,
        )
        ReportService._ensure_practitioner_in_tenant(
            db=db,
            tenant_id=tenant_id,
            practitioner_id=new_practitioner_id,
        )

        before = report.__dict__.copy()

        for field, value in update_data.items():
            setattr(report, field, value)

        db.commit()
        db.refresh(report)


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="report",
            entity_id=report.id,
            action="PATCH",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return report

    @staticmethod
    def delete_report(
        db: SASession,
        tenant_id: int,
        report_id: int,
        current_user: models.User,
    ):
        report = ReportService._get_report_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            report_id=report_id,
        )
        before = report.__dict__.copy()

        db.delete(report)
        db.commit()


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="report",
            entity_id=report_id,
            action="DELETE",
            changes={"before": before},
        )

        return
