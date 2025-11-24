from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    practitioner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)

    session_type = Column(String(50), nullable=False)  # 'online', 'in_person' vs.
    occurred_at = Column(DateTime, nullable=False)

    duration_min = Column(Integer, nullable=True)
    mood_score = Column(Integer, nullable=True)        # 1-10 arası mood değerlendirmesi
    is_first_session = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    tenant = relationship("Tenant", back_populates="session")
    practitioner = relationship("User", back_populates="session")
    client = relationship("Client", back_populates="session")
    appointment = relationship("Appointment", back_populates="session")

    notes = relationship("SessionNote", back_populates="session")
    ai_summaries = relationship("AISummary", back_populates="session")
