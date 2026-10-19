import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class HITLAction(Base):
    __tablename__ = "hitl_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(100), nullable=False)  # issue_refund, update_subscription_tier, reissue_api_key
    proposed_payload = Column(JSON, nullable=False)
    modified_payload = Column(JSON, nullable=True)
    risk_level = Column(String(20), default="HIGH")  # HIGH, CRITICAL
    risk_reason = Column(Text, nullable=False)
    status = Column(String(50), default="pending", index=True)  # pending, approved, modified, rejected
    reviewed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    ticket = relationship("Ticket", back_populates="hitl_actions")
