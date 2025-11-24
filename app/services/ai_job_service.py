from sqlalchemy.orm import Session as SASession
from fastapi import HTTPException, status

from app import models, schemas


class AiJobService:

    @staticmethod
    def _get_job_with_tenant_check(
        db: SASession,
        tenant_id: int,
        job_id: int,
    ):
        job = (
            db.query(models.AiJob)
            .filter(
                models.AiJob.id == job_id,
                models.AiJob.tenant_id == tenant_id,
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
        db: SASession,
        current_user: models.User,
        data: schemas.AiJobCreate,
    ):
        job = models.AiJob(
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
        return job

    @staticmethod
    def list_jobs(
        db: SASession,
        tenant_id: int,
    ):
        return (
            db.query(models.AiJob)
            .filter(models.AiJob.tenant_id == tenant_id)
            .order_by(models.AiJob.created_at.desc())
            .all()
        )

    @staticmethod
    def get_job(
        db: SASession,
        tenant_id: int,
        job_id: int,
    ):
        return AiJobService._get_job_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            job_id=job_id,
        )

    @staticmethod
    def update_job(
        db: SASession,
        tenant_id: int,
        job_id: int,
        data: schemas.AiJobUpdate,
    ):
        job = AiJobService._get_job_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            job_id=job_id,
        )
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(job, field, value)

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def delete_job(
        db: SASession,
        tenant_id: int,
        job_id: int,
    ):
        job = AiJobService._get_job_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            job_id=job_id,
        )
        db.delete(job)
        db.commit()
        return
