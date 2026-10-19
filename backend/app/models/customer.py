import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    company_name = Column(String(255), nullable=False)
    tier = Column(String(50), nullable=False, default="starter")  # free, starter, growth, enterprise
    stripe_customer_id = Column(String(100), nullable=True)
    active_subscription_id = Column(String(100), nullable=True)
    monthly_spend = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tickets = relationship("Ticket", back_populates="customer", cascade="all, delete-orphan")
