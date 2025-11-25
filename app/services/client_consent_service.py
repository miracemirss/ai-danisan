# app/services/client_consent_service.py

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class ClientConsentService:
    """
    Danışan Onay Formları (Client Consent) için CRUD yönetim servisi.
    """

    @staticmethod
    def _ensure_client_in_tenant(
        db: Session,
        tenant_id: int,
        client_id: int
    ) -> models.Client:
        """
        Belirtilen danışanın tenant içinde olup olmadığını doğrular.
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client not found for this tenant."
            )
        return client

    @staticmethod
    def _get_consent_with_tenant_check(
        db: Session,
        tenant_id: int,
        consent_id: int
    ) -> models.ClientConsent:
        """
        ID'ye göre onay formunu getirir.
        Tenant kontrolü, ilişkili Client üzerinden yapılır.
        """
        consent = (
            db.query(models.ClientConsent)
            .join(models.Client, models.Client.id == models.ClientConsent.client_id)
            .filter(
                models.ClientConsent.id == consent_id,
                models.Client.tenant_id == tenant_id,
            )
            .first()
        )
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent not found."
            )
        return consent

    @staticmethod
    def create_consent(
        db: Session,
        current_user: models.User,
        data: schemas.ClientConsentCreate,
    ) -> models.ClientConsent:
        """
        Yeni bir onay formu oluşturur.
        """
        tenant_id = current_user.tenant_id

        # Danışan kontrolü
        ClientConsentService._ensure_client_in_tenant(
            db, tenant_id, data.client_id
        )

        consent = models.ClientConsent(
            client_id=data.client_id,
            type=data.type,
            given_at=data.given_at,
            revoked_at=data.revoked_at,
            document_url=data.document_url,
        )

        db.add(consent)
        db.commit()
        db.refresh(consent)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ClientConsent",
            entity_id=consent.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return consent

    @staticmethod
    def list_consents(
        db: Session,
        tenant_id: int,
        client_id: Optional[int] = None,
    ) -> List[models.ClientConsent]:
        """
        Tenant'a ait onay formlarını listeler.
        client_id verilirse sadece o danışanın formları döner.
        """
        q = (
            db.query(models.ClientConsent)
            .join(models.Client, models.Client.id == models.ClientConsent.client_id)
            .filter(models.Client.tenant_id == tenant_id)
        )

        if client_id is not None:
            q = q.filter(models.ClientConsent.client_id == client_id)

        return q.order_by(models.ClientConsent.created_at.desc()).all()

    @staticmethod
    def get_consent(
        db: Session,
        tenant_id: int,
        consent_id: int,
    ) -> models.ClientConsent:
        """
        Tek bir onay formunun detaylarını getirir.
        """
        return ClientConsentService._get_consent_with_tenant_check(
            db, tenant_id, consent_id
        )

    @staticmethod
    def update_consent(
        db: Session,
        tenant_id: int,
        consent_id: int,
        data: schemas.ClientConsentUpdate,
        current_user: models.User,
    ) -> models.ClientConsent:
        """
        Onay formunu günceller.
        """
        consent = ClientConsentService._get_consent_with_tenant_check(
            db, tenant_id, consent_id
        )

        update_data = data.model_dump(exclude_unset=True)
        before = consent.__dict__.copy()

        # Eğer client_id değişiyorsa tenant kontrolü tekrar yapılmalı
        if "client_id" in update_data:
            ClientConsentService._ensure_client_in_tenant(
                db, tenant_id, update_data["client_id"]
            )

        for k, v in update_data.items():
            setattr(consent, k, v)

        db.commit()
        db.refresh(consent)

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ClientConsent",
            entity_id=consent.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": update_data
            },
        )

        return consent

    @staticmethod
    def delete_consent(
        db: Session,
        tenant_id: int,
        consent_id: int,
        current_user: models.User,
    ) -> None:
        """
        Onay formunu siler.
        """
        consent = ClientConsentService._get_consent_with_tenant_check(
            db, tenant_id, consent_id
        )
        before = consent.__dict__.copy()

        db.delete(consent)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ClientConsent",
            entity_id=consent_id,
            action="DELETE",
            changes={"before": before},
        )