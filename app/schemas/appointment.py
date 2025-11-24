# app/schemas/appointment.py

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict

AppointmentStatus = Literal["SCHEDULED", "COMPLETED", "CANCELLED", "NO_SHOW"]
AppointmentMode = Literal["ONLINE", "OFFLINE"]


class AppointmentBase(BaseModel):
    client_id: int
    practitioner_id: Optional[int] = None  # None ise current_user.id kullanacağız
    starts_at: datetime
    ends_at: datetime
    mode: AppointmentMode = "ONLINE"
    location_text: Optional[str] = None
    video_link: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Yeni randevu oluştururken kullanılacak şema."""
    pass


class AppointmentUpdate(BaseModel):
    """Randevu güncelleme için (partial) şema."""
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    mode: Optional[AppointmentMode] = None
    status: Optional[AppointmentStatus] = None
    location_text: Optional[str] = None
    video_link: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentOut(AppointmentBase):
    id: int
    tenant_id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
