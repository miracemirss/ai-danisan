# app/routers/ai_jobs.py

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.ai_job_service import AiJobService

router = APIRouter(
    prefix="/ai-jobs",
    tags=["ai_jobs"],
)


@router.post(
    "/",
    response_model=schemas.AiJobOut,
    status_code=status.HTTP_201_CREATED,
)
def create_ai_job(
    job_in: schemas.AiJobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir AI işi (Job) oluşturur.
    """
    return AiJobService.create_job(
        db=db,
        current_user=current_user,
        data=job_in,
    )


@router.get("/", response_model=List[schemas.AiJobOut])
def list_ai_jobs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Tenant'a ait tüm AI işlerini listeler.
    """
    return AiJobService.list_jobs(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/{job_id}", response_model=schemas.AiJobOut)
def get_ai_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir AI işinin detaylarını getirir.
    """
    return AiJobService.get_job(
        db=db,
        tenant_id=current_user.tenant_id,
        job_id=job_id,
    )


@router.patch("/{job_id}", response_model=schemas.AiJobOut)
def update_ai_job(
    job_id: int,
    job_in: schemas.AiJobUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    AI işini kısmi olarak günceller.
    """
    return AiJobService.update_job(
        db=db,
        tenant_id=current_user.tenant_id,
        job_id=job_id,
        data=job_in,
        current_user=current_user,  # Audit log için eklendi
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    AI işini siler.
    """
    AiJobService.delete_job(
        db=db,
        tenant_id=current_user.tenant_id,
        job_id=job_id,
        current_user=current_user,  # Audit log için eklendi
    )
    return