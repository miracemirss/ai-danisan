# app/services/ai_job_service.py

from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class AiJobService:
    """
    Yapay Zeka İşleri (AI Jobs) için CRUD yönetim servisi.
    """

    @staticmethod
    def _get_job_with_tenant_check(
        db: DbSession,
        tenant_id: int,
        job_id: int,
    ) -> models.AIJob: # ✅ Düzeltildi: AIJob
        job = (
            db.query(models.AIJob) # ✅ Düzeltildi: AIJob
            .filter(
                models.AIJob.id == job_id,
                models.AIJob.tenant_id == tenant_id,
            )
            .first()
        )
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI job not found.",
            )
        return job

    @staticmethod
    def create_job(
        db: DbSession,
        current_user: models.User,
        data: schemas.AiJobCreate,
    ) -> models.AIJob: # ✅ Düzeltildi
        job = models.AIJob( # ✅ Düzeltildi
            tenant_id=current_user.tenant_id,
            type=data.type,
            status=schemas.AiJobStatus.PENDING,
            input_ref_type=data.input_ref_type,
            input_ref_id=data.input_ref_id,
            model_name=data.model_name,
            prompt_version=data.prompt_version,
            payload=data.payload,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ai_job",
            entity_id=job.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return job

    @staticmethod
    def list_jobs(
        db: DbSession,
        tenant_id: int,
    ) -> List[models.AIJob]: # ✅ Düzeltildi
        return (
            db.query(models.AIJob) # ✅ Düzeltildi
            .filter(models.AIJob.tenant_id == tenant_id)
            .order_by(models.AIJob.created_at.desc())
            .all()
        )

    @staticmethod
    def get_job(
        db: DbSession,
        tenant_id: int,
        job_id: int,
    ) -> models.AIJob: # ✅ Düzeltildi
        return AiJobService._get_job_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            job_id=job_id,
        )

    @staticmethod
    def update_job(
        db: DbSession,
        tenant_id: int,
        job_id: int,
        data: schemas.AiJobUpdate,
        current_user: models.User,
    ) -> models.AIJob: # ✅ Düzeltildi
        job = AiJobService._get_job_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            job_id=job_id,
        )

        before = job.__dict__.copy()
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(job, field, value)

        db.commit()
        db.refresh(job)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ai_job",
            entity_id=job.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return job

    @staticmethod
    def delete_job(
        db: DbSession,
        tenant_id: int,
        job_id: int,
        current_user: models.User,
    ) -> None:
        job = AiJobService._get_job_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            job_id=job_id,
        )
        before = job.__dict__.copy()

        db.delete(job)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ai_job",
            entity_id=job_id,
            action="DELETE",
            changes={"before": before},
        )