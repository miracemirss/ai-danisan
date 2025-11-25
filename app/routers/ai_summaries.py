# app/routers/ai_summaries.py

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.ai_summary_service import AiSummaryService

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
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir AI özeti oluşturur.
    (Genellikle backend worker'ları tarafından tetiklenir, ancak API üzerinden de mümkündür).
    """
    return AiSummaryService.create_summary(
        db=db,
        current_user=current_user,
        data=summary_in,
    )


@router.get("/", response_model=List[schemas.AiSummaryOut])
def list_ai_summaries(
        session_id: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    AI özetlerini listeler.

    Filtreler:
    - **session_id**: Belirli bir seansa ait özetleri getirir.
    """
    return AiSummaryService.list_summaries(
        db=db,
        tenant_id=current_user.tenant_id,
        session_id=session_id,
    )


@router.get("/{summary_id}", response_model=schemas.AiSummaryOut)
def get_ai_summary(
        summary_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir AI özetini getirir.
    """
    return AiSummaryService.get_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        summary_id=summary_id,
    )


@router.put("/{summary_id}", response_model=schemas.AiSummaryOut)
def update_ai_summary(
        summary_id: int,
        summary_in: schemas.AiSummaryBase,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    AI özetini günceller (Tam güncelleme).
    """
    return AiSummaryService.update_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        summary_id=summary_id,
        data=summary_in,
        current_user=current_user,  # Audit log için eklendi
    )


@router.patch("/{summary_id}", response_model=schemas.AiSummaryOut)
def partial_update_ai_summary(
        summary_id: int,
        summary_in: schemas.AiSummaryUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    AI özetini kısmi olarak günceller.
    """
    return AiSummaryService.partial_update_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        summary_id=summary_id,
        data=summary_in,
        current_user=current_user,  # Audit log için eklendi
    )


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_summary(
        summary_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    AI özetini siler.
    """
    AiSummaryService.delete_summary(
        db=db,
        tenant_id=current_user.tenant_id,
        summary_id=summary_id,
        current_user=current_user,  # Audit log için eklendi
    )
    return