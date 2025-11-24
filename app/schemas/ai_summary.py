from datetime import datetime
from pydantic import BaseModel
from typing import Any


class AiSummaryBase(BaseModel):
    session_id: int
    source_note_id: int | None = None
    job_id: int | None = None
    summary_text: str
    key_points: dict[str, Any] | list[Any] | None = None
    risk_flags: dict[str, Any] | list[Any] | None = None


class AiSummaryCreate(AiSummaryBase):
    pass


class AiSummaryUpdate(BaseModel):
    session_id: int | None = None
    source_note_id: int | None = None
    job_id: int | None = None
    summary_text: str | None = None
    key_points: dict[str, Any] | list[Any] | None = None
    risk_flags: dict[str, Any] | list[Any] | None = None


class AiSummaryOut(AiSummaryBase):
    id: int
    tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True
