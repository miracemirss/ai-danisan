from sqlalchemy.orm import Session as SASession
from fastapi import HTTPException, status

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class ClientConsentService:

    # --------------------------
    # Internal helpers
    # --------------------------
    @staticmethod
    def _ensure_client_in_tenant(db: SASession, tenant_id: int, client_id: int):
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
        db: SASession,
        tenant_id: int,
        consent_id: int
    ):
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

    # --------------------------
    # CRUD
    # --------------------------

    @staticmethod
    def create_consent(
        db: SASession,
        current_user: models.User,
        data: schemas.ClientConsentCreate,
    ):
        tenant_id = current_user.tenant_id

        # tenant check
        client = ClientConsentService._ensure_client_in_tenant(
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

        # audit
        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ClientConsent",
            entity_id=consent.id,
            action="create",
            changes=data.model_dump(),
        )

        return consent

    @staticmethod
    def list_consents(
        db: SASession,
        tenant_id: int,
        client_id: int | None = None,
    ):
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
        db: SASession,
        tenant_id: int,
        consent_id: int,
    ):
        return ClientConsentService._get_consent_with_tenant_check(
            db, tenant_id, consent_id
        )

    @staticmethod
    def update_consent(
        db: SASession,
        tenant_id: int,
        consent_id: int,
        data: schemas.ClientConsentUpdate,
        current_user: models.User,
    ):
        consent = ClientConsentService._get_consent_with_tenant_check(
            db, tenant_id, consent_id
        )

        update_data = data.model_dump(exclude_unset=True)

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
            action="update",
            changes=update_data,
        )

        return consent

    @staticmethod
    def delete_consent(
        db: SASession,
        tenant_id: int,
        consent_id: int,
        current_user: models.User,
    ):
        consent = ClientConsentService._get_consent_with_tenant_check(
            db, tenant_id, consent_id
        )

        db.delete(consent)
        db.commit()

        AuditLogService.log(
            db=db,
            user=current_user,
            entity="ClientConsent",
            entity_id=consent_id,
            action="delete",
            changes=None,
        )
