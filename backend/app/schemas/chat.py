from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ChatRequest(BaseModel):
    ticket_id: str
    message: str
    customer_id: Optional[str] = None

class ChatResponse(BaseModel):
    ticket_id: str
    status: str
    reply: str
    citations: List[Dict[str, Any]] = []
    agent_trace: List[Dict[str, Any]] = []
    hitl_pending: bool = False
    hitl_action_id: Optional[str] = None
