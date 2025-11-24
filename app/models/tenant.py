from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)

    country = Column(String(100), nullable=True)
    timezone = Column(String(100), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relations
    users = relationship("User", back_populates="tenant")
    clients = relationship("Client", back_populates="tenant")
    appointment = relationship("Appointment", back_populates="tenant")
    ai_jobs = relationship("AIJob", back_populates="tenant")
    ai_summaries = relationship("AISummary", back_populates="tenant")
    reports = relationship("Report", back_populates="tenant")
    subscriptions = relationship("Subscription", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")
    session= relationship("Session", back_populates="tenant")

