from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel

class TicketMessageSchema(BaseModel):
    id: str
    ticket_id: str
    sender_type: str
    sender_name: str
    content: str
    citations: List[Any] = []
    agent_trace: List[Any] = []
    created_at: datetime

    class Config:
        from_attributes = True

class TicketBase(BaseModel):
    title: str
    severity: str = "P3"
    intent: Optional[str] = None

class TicketCreate(TicketBase):
    customer_id: Optional[str] = None
    initial_message: str

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    summary: Optional[str] = None
    assigned_agent_id: Optional[str] = None

class TicketResponse(TicketBase):
    id: str
    customer_id: Optional[str] = None
    status: str
    summary: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[TicketMessageSchema] = []

    class Config:
        from_attributes = True
