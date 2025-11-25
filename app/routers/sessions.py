# app/routers/sessions.py

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.session_service import SessionService

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)


@router.post(
    "/",
    response_model=schemas.SessionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    session_in: schemas.SessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir seans oluşturur.
    """
    return SessionService.create_session(
        db=db,
        current_user=current_user,
        data=session_in,
    )


@router.get("/", response_model=List[schemas.SessionOut])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Mevcut tenant'a ait tüm seansları listeler.
    """
    return SessionService.list_sessions(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/{session_id}", response_model=schemas.SessionOut)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    ID ile tek bir seansın detaylarını getirir.
    """
    return SessionService.get_session(
        db=db,
        tenant_id=current_user.tenant_id,
        session_id=session_id,
    )


@router.put("/{session_id}", response_model=schemas.SessionOut)
def update_session(
    session_id: int,
    session_in: schemas.SessionBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Seans bilgilerini günceller (Tam güncelleme).
    """
    return SessionService.update_session(
        db=db,
        tenant_id=current_user.tenant_id,
        session_id=session_id,
        data=session_in,
        current_user=current_user,
    )


@router.patch("/{session_id}", response_model=schemas.SessionOut)
def partial_update_session(
    session_id: int,
    session_in: schemas.SessionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Seans bilgilerini kısmi günceller.
    """
    return SessionService.partial_update_session(
        db=db,
        tenant_id=current_user.tenant_id,
        session_id=session_id,
        data=session_in,
        current_user=current_user,
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Bir seansı siler.
    """
    SessionService.delete_session(
        db=db,
        tenant_id=current_user.tenant_id,
        session_id=session_id,
        current_user=current_user,
    )
    return