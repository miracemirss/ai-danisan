from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)  # starter, pro, business
    name = Column(String(100), nullable=False)

    monthly_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="TRY", nullable=False)

    max_practitioners = Column(Integer, nullable=True)
    max_clients = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")
