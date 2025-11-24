from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class AISummary(Base):
    __tablename__ = "ai_summaries"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    source_note_id = Column(Integer, ForeignKey("session_notes.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("ai_jobs.id"), nullable=True)

    summary_text = Column(Text, nullable=False)
    key_points = Column(Text, nullable=True)  # JSON string veya newline list gibi tutulabilir
    risk_flags = Column(Text, nullable=True) # aynı şekilde

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="ai_summaries")
    session = relationship("Session", back_populates="ai_summaries")
    source_note = relationship("SessionNote", back_populates="ai_summaries")
    job = relationship("AIJob", back_populates="summaries")
