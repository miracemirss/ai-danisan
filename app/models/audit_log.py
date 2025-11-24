from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    entity_type = Column(String(100), nullable=True)  # "Client", "Session" vb.
    entity_id = Column(Integer, nullable=True)

    action = Column(String(255), nullable=False)      # "CREATE", "UPDATE", "LOGIN" vb.
    changes = Column(Text, nullable=True)             # JSON diff veya açıklama

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
