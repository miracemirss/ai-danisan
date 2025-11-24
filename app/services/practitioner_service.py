# app/services/practitioner_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app import models, schemas
from app.services.audit_log_service import AuditLogService


class PractitionerService:

    @staticmethod
    def _ensure_user_in_tenant(
        db: Session,
        tenant_id: int,
        user_id: int,
    ) -> models.User:
        user = (
            db.query(models.User)
            .filter(
                models.User.id == user_id,
                models.User.tenant_id == tenant_id,
            )
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found for this tenant.",
            )
        return user

    @staticmethod
    def _get_profile_with_tenant_check(
        db: Session,
        tenant_id: int,
        profile_id: int,
    ) -> models.PractitionerProfile:
        # practitioner_profiles'ta tenant yok, users'a join ile filtreliyoruz
        profile = (
            db.query(models.PractitionerProfile)
            .join(models.User, models.User.id == models.PractitionerProfile.user_id)
            .filter(
                models.PractitionerProfile.id == profile_id,
                models.User.tenant_id == tenant_id,
            )
            .first()
        )
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practitioner profile not found.",
            )
        return profile

    @staticmethod
    def create_profile(
        db: Session,
        current_user: models.User,
        data: schemas.PractitionerProfileCreate,
    ):
        tenant_id = current_user.tenant_id

        # 1) User gerçekten var mı ve aynı tenant'ta mı?
        PractitionerService._ensure_user_in_tenant(
            db=db,
            tenant_id=tenant_id,
            user_id=data.user_id,
        )

        # 2) Bu user için zaten profil var mı? (UNIQUE constraint)
        existing = (
            db.query(models.PractitionerProfile)
            .filter(models.PractitionerProfile.user_id == data.user_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Practitioner profile already exists for this user.",
            )

        profile = models.PractitionerProfile(
            user_id=data.user_id,
            profession=data.profession,
            license_number=data.license_number,
            bio=data.bio,
            experience_years=data.experience_years,
            specialties=data.specialties,
            session_duration_min=data.session_duration_min or 50,
        )

        db.add(profile)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error while creating practitioner profile.",
            )

        db.refresh(profile)


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="practitioner_profile",
            entity_id=profile.id,
            action="CREATE",
            changes=data.model_dump(),
        )

        return profile

    @staticmethod
    def list_profiles(db: Session, tenant_id: int):
        # practitioner_profiles'ta tenant_id yok, users'tan join ile filtrele
        return (
            db.query(models.PractitionerProfile)
            .join(models.User, models.User.id == models.PractitionerProfile.user_id)
            .filter(models.User.tenant_id == tenant_id)
            .all()
        )

    @staticmethod
    def get_profile(db: Session, tenant_id: int, profile_id: int):
        return PractitionerService._get_profile_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            profile_id=profile_id,
        )

    @staticmethod
    def update_profile(
        db: Session,
        tenant_id: int,
        profile_id: int,
        data: schemas.PractitionerProfileBase,
        current_user: models.User,
    ):
        profile = PractitionerService._get_profile_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            profile_id=profile_id,
        )

        before = profile.__dict__.copy()

        # Eğer şemada user_id varsa ve değiştiriliyorsa tenant kontrolü yap
        update_data = data.model_dump()
        new_user_id = update_data.get("user_id", profile.user_id)
        if new_user_id != profile.user_id:
            PractitionerService._ensure_user_in_tenant(
                db=db,
                tenant_id=tenant_id,
                user_id=new_user_id,
            )

        for field, value in update_data.items():
            setattr(profile, field, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error while updating practitioner profile.",
            )

        db.refresh(profile)


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="practitioner_profile",
            entity_id=profile.id,
            action="UPDATE",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return profile

    @staticmethod
    def partial_update_profile(
        db: Session,
        tenant_id: int,
        profile_id: int,
        data: schemas.PractitionerProfileUpdate,
        current_user: models.User,
    ):
        profile = PractitionerService._get_profile_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            profile_id=profile_id,
        )
        update_data = data.model_dump(exclude_unset=True)

        before = profile.__dict__.copy()

        # user_id patch ile değişiyorsa tenant kontrolü yap
        new_user_id = update_data.get("user_id", profile.user_id)
        if new_user_id != profile.user_id:
            PractitionerService._ensure_user_in_tenant(
                db=db,
                tenant_id=tenant_id,
                user_id=new_user_id,
            )

        for field, value in update_data.items():
            setattr(profile, field, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error while updating practitioner profile.",
            )

        db.refresh(profile)


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="practitioner_profile",
            entity_id=profile.id,
            action="PATCH",
            changes={
                "before": before,
                "after": update_data,
            },
        )

        return profile

    @staticmethod
    def delete_profile(
        db: Session,
        tenant_id: int,
        profile_id: int,
        current_user: models.User,
    ):
        profile = PractitionerService._get_profile_with_tenant_check(
            db=db,
            tenant_id=tenant_id,
            profile_id=profile_id,
        )
        before = profile.__dict__.copy()

        db.delete(profile)
        db.commit()


        AuditLogService.log(
            db=db,
            user=current_user,
            entity="practitioner_profile",
            entity_id=profile_id,
            action="DELETE",
            changes={"before": before},
        )

        return
