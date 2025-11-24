from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as SASession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.ai_job_service import AiJobService
from app import schemas, models

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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AiJobService.create_job(
        db=db,
        current_user=current_user,
        data=job_in,
    )


@router.get("/", response_model=list[schemas.AiJobOut])
def list_ai_jobs(
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AiJobService.list_jobs(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/{job_id}", response_model=schemas.AiJobOut)
def get_ai_job(
    job_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AiJobService.get_job(
        db=db,
        tenant_id=current_user.tenant_id,
        job_id=job_id,
    )


@router.patch("/{job_id}", response_model=schemas.AiJobOut)
def update_ai_job(
    job_id: int,
    job_in: schemas.AiJobUpdate,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AiJobService.update_job(
        db=db,
        tenant_id=current_user.tenant_id,
        job_id=job_id,
        data=job_in,
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_job(
    job_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    AiJobService.delete_job(
        db=db,
        tenant_id=current_user.tenant_id,
        job_id=job_id,
    )
    return
