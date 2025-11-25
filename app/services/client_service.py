# app/services/client_service.py

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class ClientService:
    """
    Danışan (Client) kayıtları için CRUD (Oluşturma, Okuma, Güncelleme, Silme)
    işlemlerini yöneten servis sınıfı.
    """

    @staticmethod
    def create_client(
        db: Session,
        tenant_id: int,
        data: schemas.ClientCreate,
        current_user: models.User,
    ) -> models.Client:
        """
        Yeni bir danışan oluşturur.
        """
        client = models.Client(
            tenant_id=tenant_id,
            **data.model_dump(exclude_unset=True),
        )

        db.add(client)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this email already exists for this tenant.",
            )

        db.refresh(client)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="client",
            entity_id=client.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return client

    @staticmethod
    def list_clients(db: Session, tenant_id: int) -> List[models.Client]:
        """
        Tenant'a ait tüm danışanları isim sırasına göre listeler.
        """
        return (
            db.query(models.Client)
            .filter(models.Client.tenant_id == tenant_id)
            .order_by(models.Client.first_name, models.Client.last_name)
            .all()
        )

    @staticmethod
    def get_client(db: Session, tenant_id: int, client_id: int) -> models.Client:
        """
        ID'ye göre tek bir danışan detayını getirir.
        """
        client = (
            db.query(models.Client)
            .filter(
                models.Client.id == client_id,
                models.Client.tenant_id == tenant_id,
            )
            .first()
        )
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return client

    @staticmethod
    def update_client(
        db: Session,
        tenant_id: int,
        client_id: int,
        data: schemas.ClientCreate,
        current_user: models.User,
    ) -> models.Client:
        """
        Danışan bilgilerini günceller (Tam güncelleme - PUT).
        """
        client = ClientService.get_client(db, tenant_id, client_id)
        before = client.__dict__.copy()

        # Tüm alanları güncelle
        for field, value in data.model_dump().items():
            setattr(client, field, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this email already exists for this tenant.",
            )

        db.refresh(client)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="client",
            entity_id=client.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": data.model_dump(),
            },
        )

        return client

    @staticmethod
    def partial_update_client(
        db: Session,
        tenant_id: int,
        client_id: int,
        data: schemas.ClientUpdate,
        current_user: models.User,
    ) -> models.Client:
        """
        Danışan bilgilerini kısmi olarak günceller (PATCH).
        """
        client = ClientService.get_client(db, tenant_id, client_id)
        before = client.__dict__.copy()

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(client, field, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this email already exists for this tenant.",
            )

        db.refresh(client)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="client",
            entity_id=client.id,
            action="PATCH",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return client

    @staticmethod
    def delete_client(
        db: Session,
        tenant_id: int,
        client_id: int,
        current_user: models.User,
    ) -> None:
        """
        Bir danışanı siler.
        """
        client = ClientService.get_client(db, tenant_id, client_id)
        before = client.__dict__.copy()

        db.delete(client)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="client",
            entity_id=client.id,
            action="DELETE",
            changes={"before": before},
        )