# app/schemas/practitioner.py
from pydantic import BaseModel
from enum import Enum
from typing import Any


class Profession(str, Enum):
    PSYCHOLOGIST = "PSYCHOLOGIST"
    PSYCHIATRIST = "PSYCHIATRIST"
    DIETITIAN = "DIETITIAN"
    COACH = "COACH"
    # PostgreSQL'deki "profession" enum'una ne eklediysen onları buraya da ekle


class PractitionerProfileBase(BaseModel):
    profession: Profession
    license_number: str | None = None
    bio: str | None = None
    experience_years: int | None = None
    specialties: dict[str, Any] | list[Any] | None = None
    session_duration_min: int | None = 50


class PractitionerProfileCreate(PractitionerProfileBase):
    # user_id create'de zorunlu, update'de değişmeyecek
    user_id: int


class PractitionerProfileUpdate(BaseModel):
    profession: Profession | None = None
    license_number: str | None = None
    bio: str | None = None
    experience_years: int | None = None
    specialties: dict[str, Any] | list[Any] | None = None
    session_duration_min: int | None = None


class PractitionerProfileOut(PractitionerProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
        # Pydantic v1 ise:
        # orm_mode = True
