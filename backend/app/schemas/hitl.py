from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class HITLReviewRequest(BaseModel):
    decision: str  # APPROVED, MODIFIED, REJECTED
    modified_payload: Optional[Dict[str, Any]] = None
    review_notes: Optional[str] = None

class HITLActionResponse(BaseModel):
    id: str
    ticket_id: str
    action_type: str
    proposed_payload: Dict[str, Any]
    modified_payload: Optional[Dict[str, Any]] = None
    risk_level: str
    risk_reason: str
    status: str
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
