from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import Any


class AiJobType(str, Enum):
    SESSION_SUMMARY = "SESSION_SUMMARY"
    NOTE_SUMMARY = "NOTE_SUMMARY"
    RISK_ANALYSIS = "RISK_ANALYSIS"
    # PostgreSQL'deki ai_job_type enum değerlerini buraya birebir ekle


class AiJobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    # DB enum ile birebir uyumlu olmalı


class AiJobBase(BaseModel):
    type: AiJobType
    input_ref_type: str
    input_ref_id: int
    model_name: str | None = None
    prompt_version: str | None = None
    payload: dict[str, Any] | list[Any] | None = None


class AiJobCreate(AiJobBase):
    # status, created_at backend tarafından set edilecek
    pass


class AiJobUpdate(BaseModel):
    status: AiJobStatus | None = None
    error_message: str | None = None
    # istersen model_name / prompt_version / payload da güncellenebilir:
    model_name: str | None = None
    prompt_version: str | None = None
    payload: dict[str, Any] | list[Any] | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class AiJobOut(AiJobBase):
    id: int
    tenant_id: int
    status: AiJobStatus
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    class Config:
        from_attributes = True
        # Pydantic v1:
        # orm_mode = True
