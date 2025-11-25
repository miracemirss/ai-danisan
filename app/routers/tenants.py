# app/routers/tenants.py

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.tenant_service import TenantService

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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Yeni bir tenant (işletme/klinik) oluşturur.
    Genellikle sadece Sistem Yöneticileri (Super Admin) tarafından kullanılmalıdır.
    """
    return TenantService.create_tenant(
        db=db,
        data=tenant_in,
        current_user=current_user,
    )


@router.get("/", response_model=List[schemas.TenantOut])
def list_tenants(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Sistemdeki tüm tenant'ları listeler.
    """
    return TenantService.list_tenants(db=db)


@router.get("/me", response_model=schemas.TenantOut)
def get_my_tenant(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Oturum açmış kullanıcının bağlı olduğu tenant bilgilerini döner.
    """
    return TenantService.get_current_user_tenant(
        db=db,
        current_user=current_user,
    )


@router.get("/{tenant_id}", response_model=schemas.TenantOut)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Belirli bir tenant'ın detaylarını ID ile getirir.
    """
    return TenantService.get_tenant(db=db, tenant_id=tenant_id)


@router.put("/{tenant_id}", response_model=schemas.TenantOut)
def update_tenant(
    tenant_id: int,
    tenant_in: schemas.TenantBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Tenant bilgilerini günceller (Tam güncelleme).
    """
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Tenant bilgilerini kısmi olarak günceller (Örn: Sadece isim değişimi).
    """
    return TenantService.partial_update_tenant(
        db=db,
        tenant_id=tenant_id,
        data=tenant_in,
        current_user=current_user,
    )


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Bir tenant'ı ve ilişkili verilerini siler.
    Dikkatli kullanılmalıdır.
    """
    TenantService.delete_tenant(
        db=db,
        tenant_id=tenant_id,
        current_user=current_user,
    )
    return