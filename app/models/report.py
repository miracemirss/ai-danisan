from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    practitioner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    pdf_url = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="reports")
    client = relationship("Client", back_populates="reports")
    practitioner = relationship("User", back_populates="reports")
