from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False, default="OWNER") # owner / practitioner / assistant vs.
    is_active = Column(Boolean, default=True, nullable=False)

    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")
    practitioner_profile = relationship(
        "PractitionerProfile", back_populates="user", uselist=False
    )


    appointment = relationship("Appointment", back_populates="practitioner")
    primary_clients = relationship(
        "Client",
        back_populates="primary_practitioner",
        foreign_keys="Client.primary_practitioner_id",
    )
    audit_logs = relationship("AuditLog", back_populates="user")
    session = relationship("Session", back_populates="practitioner")
    session_notes = relationship("SessionNote", back_populates="author")
    reports= relationship("Report", back_populates="practitioner")