from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    practitioner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)

    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)

    status = Column(String(50), nullable=False, default="scheduled")  # scheduled/cancelled/completed
    mode = Column(String(50), nullable=True)                          # online / in_person vs.

    location_text = Column(String(255), nullable=True)
    video_link = Column(String(255), nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="appointment")
    practitioner = relationship("User", back_populates="appointment")
    client = relationship("Client", back_populates="appointment")
    session = relationship("Session", back_populates="appointment",uselist=False)