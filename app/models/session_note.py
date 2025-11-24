from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.database import Base


class SessionNote(Base):
    __tablename__ = "session_notes"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    type = Column(String(50), nullable=False)  # "manual", "ai", "followup", vb.
    content = Column(Text, nullable=False)

    is_private = Column(Boolean, default=False)  # sadece uzman görebilir mi?
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("Session", back_populates="notes")
    author = relationship("User", back_populates="session_notes")
    ai_summaries = relationship("AISummary", back_populates="source_note")
