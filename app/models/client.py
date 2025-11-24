from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    primary_practitioner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    gender = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)

    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    address = Column(Text, nullable=True)

    notes = Column(Text, nullable=True)
    status = Column(String(50), default="active")     # active / archived vs.

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="clients")
    primary_practitioner = relationship("User", back_populates="primary_clients")

    appointment = relationship("Appointment", back_populates="client")
    consents = relationship("ClientConsent", back_populates="client")
    session = relationship("Session", back_populates="client")
    reports= relationship("Report", back_populates="client")
