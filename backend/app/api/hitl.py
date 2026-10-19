"""
Human-in-the-Loop (HITL) Review Action Center API Routes.
Provides:
  - GET /api/v1/hitl/queue (List pending high-risk actions)
  - POST /api/v1/hitl/{id}/review (Approve / Modify / Reject)
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.hitl import HITLAction
from backend.app.models.ticket import Ticket, TicketMessage
from backend.app.models.audit import AuditLog
from backend.app.schemas.hitl import HITLActionResponse, HITLReviewRequest
from backend.app.agent_core.tools.mcp_tools import issue_refund, update_subscription_tier

router = APIRouter(prefix="/hitl", tags=["Human-in-the-Loop"])

@router.get("/queue", response_model=List[HITLActionResponse])
async def list_pending_hitl_actions(db: AsyncSession = Depends(get_db)):
    """List all actions flagged by the agent core requiring human specialist review."""
    query = select(HITLAction).filter(HITLAction.status == "pending").order_by(desc(HITLAction.created_at))
    res = await db.execute(query)
    return res.scalars().all()

@router.post("/{action_id}/review", response_model=HITLActionResponse)
async def review_hitl_action(
    action_id: str,
    payload: HITLReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Operator sign-off endpoint:
      - APPROVED: Executes the proposed MCP operational mutation.
      - MODIFIED: Executes the modified payload supplied by the operator.
      - REJECTED: Halts the mutation and logs the reason.
    """
    res = await db.execute(select(HITLAction).filter(HITLAction.id == action_id))
    hitl_act = res.scalars().first()
    if not hitl_act:
        raise HTTPException(status_code=404, detail="HITL action not found")

    decision = payload.decision.upper()
    if decision not in ("APPROVED", "MODIFIED", "REJECTED"):
        raise HTTPException(status_code=400, detail="Decision must be APPROVED, MODIFIED, or REJECTED")

    hitl_act.status = decision.lower()
    hitl_act.reviewed_at = datetime.utcnow()
    hitl_act.review_notes = payload.review_notes
    if payload.modified_payload:
        hitl_act.modified_payload = payload.modified_payload

    # Fetch associated ticket
    t_res = await db.execute(select(Ticket).filter(Ticket.id == hitl_act.ticket_id))
    ticket = t_res.scalars().first()

    exec_result = {}
    if decision in ("APPROVED", "MODIFIED"):
        exec_params = payload.modified_payload if (decision == "MODIFIED" and payload.modified_payload) else hitl_act.proposed_payload
        
        # Execute tool mutation
        if hitl_act.action_type == "issue_refund":
            exec_result = issue_refund(
                invoice_id=exec_params.get("invoice_id", "INV-UNKNOWN"),
                amount=float(exec_params.get("amount", 0.0)),
                reason=payload.review_notes or exec_params.get("reason", "Operator authorized refund")
            )
        elif hitl_act.action_type == "update_subscription_tier":
            exec_result = update_subscription_tier(
                customer_id=exec_params.get("customer_id", "cust_default"),
                new_tier=exec_params.get("new_tier", "enterprise")
            )
        else:
            exec_result = {"status": "completed", "action": hitl_act.action_type, "params": exec_params}

        if ticket:
            ticket.status = "resolved"
            refund_amt = exec_params.get("amount", "")
            ticket.summary = f"Operator {decision.lower()} action '{hitl_act.action_type}' for {refund_amt}. Mutation executed successfully."
            
            # Post confirmation message
            conf_msg = TicketMessage(
                ticket_id=ticket.id,
                sender_type="system",
                sender_name="System / Human Specialist Sign-off",
                content=f"Human Support Specialist has {decision} this action. The operational mutation has been executed. Confirmation: {exec_result.get('refund_id') or 'Processed'}.",
                created_at=datetime.utcnow()
            )
            db.add(conf_msg)
    else:
        # Rejected
        if ticket:
            ticket.status = "escalated"
            ticket.summary = f"Operator rejected action '{hitl_act.action_type}'. Reason: {payload.review_notes}"
            rej_msg = TicketMessage(
                ticket_id=ticket.id,
                sender_type="system",
                sender_name="System / Human Specialist Sign-off",
                content=f"Proposed action was reviewed and rejected by human support specialist. Notes: {payload.review_notes or 'Requires manual escalation'}.",
                created_at=datetime.utcnow()
            )
            db.add(rej_msg)

    # Log to Audit Trail
    audit = AuditLog(
        ticket_id=hitl_act.ticket_id,
        actor="Human Support Specialist",
        event_type=f"hitl_{decision.lower()}",
        details={
            "action_id": hitl_act.id,
            "action_type": hitl_act.action_type,
            "decision": decision,
            "notes": payload.review_notes,
            "execution_result": exec_result
        },
        created_at=datetime.utcnow()
    )
    db.add(audit)
    await db.commit()

    return hitl_act
