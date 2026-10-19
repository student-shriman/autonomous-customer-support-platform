import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from backend.app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True, index=True)
    actor = Column(String(100), nullable=False)  # system, agent_supervisor, agent_resolution, operator_sarah
    event_type = Column(String(100), nullable=False)  # state_transition, tool_executed, hitl_interrupt, hitl_reviewed
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
