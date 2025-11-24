from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as SASession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.ai_summary_service import AiSummaryService
from app import schemas, models

router = APIRouter(
    prefix="/ai-summaries",
    tags=["ai_summaries"],
)


@router.post(
    "/",
    response_model=schemas.AiSummaryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_ai_summary(
    summary_in: schemas.AiSummaryCreate,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Gerçekte bunu genelde backend/worker üretir,
    # ama burada tam CRUD veriyoruz.
    return AiSummaryService.create_summary(
        db=db,
        current_user=current_user,
        data=summary_in,
    )


@router.get("/", response_model=list[schemas.AiSummaryOut])
def list_ai_summaries(
    session_id: int | None = None,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AiSummaryService.list_summaries(
        db=db,
        tenant_id=current_user.tenant_id,
        session_id=session_id,
    )


@router.get("/{summary_id}", response_model=schemas.AiSummaryOut)
def get_ai_summary(
    summary_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AiSummaryService.get_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        summary_id=summary_id,
    )


@router.put("/{summary_id}", response_model=schemas.AiSummaryOut)
def update_ai_summary(
    summary_id: int,
    summary_in: schemas.AiSummaryBase,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AiSummaryService.update_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        summary_id=summary_id,
        data=summary_in,
    )


@router.patch("/{summary_id}", response_model=schemas.AiSummaryOut)
def partial_update_ai_summary(
    summary_id: int,
    summary_in: schemas.AiSummaryUpdate,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return AiSummaryService.partial_update_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        summary_id=summary_id,
        data=summary_in,
    )


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_summary(
    summary_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    AiSummaryService.delete_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        summary_id=summary_id,
    )
    return
