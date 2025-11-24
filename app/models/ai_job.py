from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    type = Column(String(50), nullable=False)          # örn: "summary", "risk_flags"
    status = Column(String(50), nullable=False)        # queued / running / done / failed

    input_ref_type = Column(String(50), nullable=False)  # "session", "session_note" vs.
    input_ref_id = Column(Integer, nullable=False)

    model_name = Column(String(100), nullable=True)
    prompt_version = Column(String(50), nullable=True)

    payload = Column(Text, nullable=True)             # ham prompt / input
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # ilişkiler (Tenant, AISummary) – diğer modelleri yazınca aktif olur
    tenant = relationship("Tenant", back_populates="ai_jobs", lazy="joined", overlaps="ai_jobs")
    summaries = relationship("AISummary", back_populates="job", lazy="selectin")
