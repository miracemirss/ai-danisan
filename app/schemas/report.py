# app/schemas/report.py

from datetime import date, datetime
from pydantic import BaseModel, field_validator


class ReportBase(BaseModel):
    client_id: int
    practitioner_id: int
    period_start: date | None = None
    period_end: date | None = None
    title: str
    content: str
    pdf_url: str | None = None

    @field_validator("period_end")
    @classmethod
    def validate_period(cls, v, info):
        # period_start varsa, period_end ondan küçük olmasın
        if v is None:
            return v
        period_start = info.data.get("period_start")
        if period_start and v < period_start:
            raise ValueError("period_end cannot be before period_start")
        return v


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    client_id: int | None = None
    practitioner_id: int | None = None
    period_start: date | None = None
    period_end: date | None = None
    title: str | None = None
    content: str | None = None
    pdf_url: str | None = None

    @field_validator("period_end")
    @classmethod
    def validate_period(cls, v, info):
        if v is None:
            return v
        period_start = info.data.get("period_start")
        if period_start and v < period_start:
            raise ValueError("period_end cannot be before period_start")
        return v


class ReportOut(ReportBase):
    id: int
    tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        # Pydantic v1 ise:
        # orm_mode = True
