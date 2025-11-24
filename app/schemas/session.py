# app/schemas/session.py

from datetime import datetime
from pydantic import BaseModel, field_validator
from enum import Enum


class SessionType(str, Enum):
    THERAPY = "THERAPY"
    # PostgreSQL'deki "session_type" enum'unun tüm değerlerini buraya ekle:
    # CHECKIN = "CHECKIN"
    # COACHING = "COACHING"
    # ASSESSMENT = "ASSESSMENT"
    # vs.


class SessionBase(BaseModel):
    practitioner_id: int
    client_id: int
    appointment_id: int | None = None
    session_type: SessionType | None = None  # None gelirse DB default THERAPY
    occurred_at: datetime
    duration_min: int | None = None
    mood_score: int | None = None
    is_first_session: bool | None = None

    @field_validator("duration_min")
    @classmethod
    def validate_duration(cls, v):
        if v is not None and v < 0:
            raise ValueError("duration_min must be >= 0")
        return v

    @field_validator("mood_score")
    @classmethod
    def validate_mood(cls, v):
        if v is not None and (v < 0 or v > 10):
            # kendi skalan neyse ona göre ayarlarsın
            raise ValueError("mood_score must be between 0 and 10")
        return v


class SessionCreate(SessionBase):
    # şimdilik ekstra alan yok
    pass


class SessionUpdate(BaseModel):
    practitioner_id: int | None = None
    client_id: int | None = None
    appointment_id: int | None = None
    session_type: SessionType | None = None
    occurred_at: datetime | None = None
    duration_min: int | None = None
    mood_score: int | None = None
    is_first_session: bool | None = None

    @field_validator("duration_min")
    @classmethod
    def validate_duration(cls, v):
        if v is not None and v < 0:
            raise ValueError("duration_min must be >= 0")
        return v

    @field_validator("mood_score")
    @classmethod
    def validate_mood(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError("mood_score must be between 0 and 10")
        return v


class SessionOut(SessionBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # Pydantic v1 ise:
        # orm_mode = True
