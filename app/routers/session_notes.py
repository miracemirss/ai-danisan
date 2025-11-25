# app/routers/session_notes.py

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.session_note_service import SessionNoteService

router = APIRouter(
    prefix="/session-notes",
    tags=["session_notes"],
)


@router.post(
    "/",
    response_model=schemas.SessionNoteOut,
    status_code=status.HTTP_201_CREATED,
)
def create_session_note(
        note_in: schemas.SessionNoteCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir seans notu oluşturur.
    """
    return SessionNoteService.create_note(
        db=db,
        current_user=current_user,
        data=note_in,
    )


@router.get("/", response_model=List[schemas.SessionNoteOut])
def list_session_notes(
        session_id: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Seans notlarını listeler.

    Filtreler:
    - **session_id**: Eğer verilirse, sadece o seansa ait notlar döner.
    - Verilmezse, tenant'a ait tüm notlar döner.
    """
    return SessionNoteService.list_notes(
        db=db,
        tenant_id=current_user.tenant_id,
        session_id=session_id,
    )


@router.get("/{note_id}", response_model=schemas.SessionNoteOut)
def get_session_note(
        note_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir seans notunun detaylarını getirir.
    """
    return SessionNoteService.get_note(
        db=db,
        tenant_id=current_user.tenant_id,
        note_id=note_id,
    )


@router.put("/{note_id}", response_model=schemas.SessionNoteOut)
def update_session_note(
        note_id: int,
        note_in: schemas.SessionNoteBase,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Seans notunu günceller (Tam güncelleme).
    """
    return SessionNoteService.update_note(
        db=db,
        tenant_id=current_user.tenant_id,
        note_id=note_id,
        data=note_in,
        current_user=current_user,
    )


@router.patch("/{note_id}", response_model=schemas.SessionNoteOut)
def partial_update_session_note(
        note_id: int,
        note_in: schemas.SessionNoteUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Seans notunu kısmi olarak günceller.
    """
    return SessionNoteService.partial_update_note(
        db=db,
        tenant_id=current_user.tenant_id,
        note_id=note_id,
        data=note_in,
        current_user=current_user,
    )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session_note(
        note_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
):
    """
    Seans notunu siler.
    """
    SessionNoteService.delete_note(
        db=db,
        tenant_id=current_user.tenant_id,
        note_id=note_id,
        current_user=current_user,
    )
    return