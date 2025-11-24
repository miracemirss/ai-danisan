# app/routers/tenants.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as SASession

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.tenant_service import TenantService
from app import schemas, models

router = APIRouter(
    prefix="/tenants",
    tags=["tenants"],
)


@router.post(
    "/",
    response_model=schemas.TenantOut,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    tenant_in: schemas.TenantCreate,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Rol check istersen:
    # if current_user.role != models.UserRole.ADMIN:
    #     raise HTTPException(status_code=403, detail="Not allowed to create tenants")
    return TenantService.create_tenant(
        db=db,
        data=tenant_in,
        current_user=current_user,
    )


@router.get("/", response_model=list[schemas.TenantOut])
def list_tenants(
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # if current_user.role != models.UserRole.ADMIN:
    #     raise HTTPException(status_code=403, detail="Not allowed to list tenants")
    return TenantService.list_tenants(db=db)


@router.get("/me", response_model=schemas.TenantOut)
def get_my_tenant(
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Login olan kullanıcının bağlı olduğu tenant'ı döner.
    """
    return TenantService.get_current_user_tenant(
        db=db,
        current_user=current_user,
    )


@router.get("/{tenant_id}", response_model=schemas.TenantOut)
def get_tenant(
    tenant_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Rol kontrolü istersen burada
    return TenantService.get_tenant(db=db, tenant_id=tenant_id)


@router.put("/{tenant_id}", response_model=schemas.TenantOut)
def update_tenant(
    tenant_id: int,
    tenant_in: schemas.TenantBase,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return TenantService.update_tenant(
        db=db,
        tenant_id=tenant_id,
        data=tenant_in,
        current_user=current_user,
    )


@router.patch("/{tenant_id}", response_model=schemas.TenantOut)
def partial_update_tenant(
    tenant_id: int,
    tenant_in: schemas.TenantUpdate,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return TenantService.partial_update_tenant(
        db=db,
        tenant_id=tenant_id,
        data=tenant_in,
        current_user=current_user,
    )


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: int,
    db: SASession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    TenantService.delete_tenant(
        db=db,
        tenant_id=tenant_id,
        current_user=current_user,
    )
    return
