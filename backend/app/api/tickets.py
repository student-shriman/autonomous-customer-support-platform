"""
Ticket Lifecycle API Routes.
Provides:
  - GET /api/v1/tickets (Triage feed)
  - GET /api/v1/tickets/{id} (Ticket deep-dive & message history)
  - POST /api/v1/tickets (New customer ticket creation)
"""

from typing import List, Optional
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.ticket import Ticket, TicketMessage
from backend.app.models.customer import CustomerProfile
from backend.app.schemas.ticket import TicketCreate, TicketResponse
from backend.app.services.guardrail_service import validate_input
from backend.app.agent_core.graph import support_graph
from langchain_core.messages import HumanMessage

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("", response_model=List[TicketResponse])
async def list_tickets(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    query = select(Ticket).options(selectinload(Ticket.messages)).order_by(desc(Ticket.created_at)).limit(limit)
    if status:
        query = query.filter(Ticket.status == status)
    if severity:
        query = query.filter(Ticket.severity == severity)
        
    res = await db.execute(query)
    return res.scalars().all()

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    query = select(Ticket).options(selectinload(Ticket.messages)).filter(Ticket.id == ticket_id)
    res = await db.execute(query)
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("", response_model=TicketResponse)
async def create_ticket(payload: TicketCreate, db: AsyncSession = Depends(get_db)):
    # 1. Validate Input through Guardrails
    is_valid, sanitized_text = validate_input(payload.initial_message)
    if not is_valid:
        raise HTTPException(status_code=400, detail=sanitized_text)

    # 2. Find or create customer
    cust_id = payload.customer_id or "cust_acme"
    
    # 3. Create Ticket record
    ticket = Ticket(
        id=f"TK-{uuid.uuid4().hex[:6].upper()}",
        customer_id=cust_id,
        title=payload.title,
        status="open",
        severity=payload.severity or "P3",
        created_at=datetime.utcnow()
    )
    db.add(ticket)
    await db.flush()

    # 4. Save Customer Message
    user_msg = TicketMessage(
        id=str(uuid.uuid4()),
        ticket_id=ticket.id,
        sender_type="customer",
        sender_name="Alex Miller",
        content=sanitized_text,
        created_at=datetime.utcnow()
    )
    db.add(user_msg)
    await db.commit()

    # Reload with relationships
    return await get_ticket(ticket.id, db)
