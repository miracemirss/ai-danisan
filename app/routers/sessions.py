# app/routers/sessions.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as SASession
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.session_service import SessionService
from app import schemas, models

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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SessionService.create_session(
        db=db,
        current_user=current_user,
        data=session_in,
    )


@router.get("/", response_model=list[schemas.SessionOut])
def list_sessions(
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SessionService.list_sessions(
        db=db,
        tenant_id=current_user.tenant_id,
    )


@router.get("/{session_id}", response_model=schemas.SessionOut)
def get_session(
    session_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return SessionService.get_session(
        db=db,
        tenant_id=current_user.tenant_id,
        session_id=session_id,
    )


@router.put("/{session_id}", response_model=schemas.SessionOut)
def update_session(
    session_id: int,
    session_in: schemas.SessionBase,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
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
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    SessionService.delete_session(
        db=db,
        tenant_id=current_user.tenant_id,
        session_id=session_id,
        current_user=current_user,
    )
    return
