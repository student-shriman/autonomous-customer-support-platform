"""
Chat & Real-Time SSE Streaming API Routes.
Provides:
  - POST /api/v1/chat (Standard synchronous agent invocation)
  - POST /api/v1/chat/stream (Real-time Server-Sent Events token & trace stream)
"""

import json
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db, AsyncSessionLocal
from backend.app.models.ticket import Ticket, TicketMessage
from backend.app.models.hitl import HITLAction
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.guardrail_service import validate_input
from backend.app.agent_core.graph import support_graph
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def send_chat_message(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. Guardrail validation
    is_valid, sanitized_text = validate_input(payload.message)
    if not is_valid:
        raise HTTPException(status_code=400, detail=sanitized_text)

    # 2. Get Ticket
    res = await db.execute(select(Ticket).filter(Ticket.id == payload.ticket_id))
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # 3. Save incoming user message
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

    # 4. Invoke LangGraph multi-agent flow
    initial_state = {
        "messages": [HumanMessage(content=sanitized_text)],
        "ticket_id": ticket.id,
        "customer_id": ticket.customer_id or "cust_default",
        "agent_trace": [],
        "retrieved_docs": [],
        "diagnostic_findings": []
    }

    config = {"configurable": {"thread_id": ticket.id}}
    final_state = await asyncio.to_thread(support_graph.invoke, initial_state, config=config)

    # 5. Extract output
    messages = final_state.get("messages", [])
    reply_content = messages[-1].content if messages else "Inquiry processed."
    agent_trace = final_state.get("agent_trace", [])
    retrieved_docs = final_state.get("retrieved_docs", [])
    citations = [{"title": d["title"], "id": d["id"], "score": d.get("rerank_score")} for d in retrieved_docs]
    action_risk_level = final_state.get("action_risk_level", "LOW")
    hitl_pending = action_risk_level == "HIGH"
    proposed_action = final_state.get("proposed_action") or {}

    hitl_action_id = None
    if hitl_pending:
        # Create pending HITL Action record in database
        hitl_act = HITLAction(
            id=f"act_hitl_{uuid.uuid4().hex[:8]}",
            ticket_id=ticket.id,
            action_type=proposed_action.get("type", "operational_action"),
            proposed_payload=proposed_action.get("parameters", {}),
            risk_level="HIGH",
            risk_reason=proposed_action.get("reason", "Action requires human approval"),
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(hitl_act)
        ticket.status = "pending_hitl"
        hitl_action_id = hitl_act.id
    else:
        ticket.status = "investigating"

    # Update ticket severity and intent if classified
    if final_state.get("severity"):
        ticket.severity = final_state.get("severity")
    if final_state.get("intent"):
        ticket.intent = final_state.get("intent")

    # 6. Save Agent Response Message
    agent_msg = TicketMessage(
        id=str(uuid.uuid4()),
        ticket_id=ticket.id,
        sender_type="agent",
        sender_name="Autonomous Support Agent",
        content=reply_content,
        citations=citations,
        agent_trace=agent_trace,
        created_at=datetime.utcnow()
    )
    db.add(agent_msg)
    await db.commit()

    return {
        "ticket_id": ticket.id,
        "status": ticket.status,
        "reply": reply_content,
        "citations": citations,
        "agent_trace": agent_trace,
        "hitl_pending": hitl_pending,
        "hitl_action_id": hitl_action_id
    }

@router.post("/stream")
async def stream_chat_message(payload: ChatRequest):
    """Server-Sent Events (SSE) streaming endpoint."""
    async def event_generator():
        yield f"data: {json.dumps({'event': 'start', 'ticket_id': payload.ticket_id})}\n\n"
        await asyncio.sleep(0.1)

        async with AsyncSessionLocal() as session:
            # 1. Validate
            is_valid, sanitized_text = validate_input(payload.message)
            if not is_valid:
                yield f"data: {json.dumps({'event': 'error', 'message': sanitized_text})}\n\n"
                return

            # 2. Get ticket
            res = await session.execute(select(Ticket).filter(Ticket.id == payload.ticket_id))
            ticket = res.scalars().first()
            if not ticket:
                yield f"data: {json.dumps({'event': 'error', 'message': 'Ticket not found'})}\n\n"
                return

            yield f"data: {json.dumps({'event': 'thought', 'agent': 'Supervisor Agent', 'thought': 'Analyzing customer message and classifying severity...'})}\n\n"
            await asyncio.sleep(0.3)

            # Invoke Agent Core
            initial_state = {
                "messages": [HumanMessage(content=sanitized_text)],
                "ticket_id": ticket.id,
                "customer_id": ticket.customer_id or "cust_default",
                "agent_trace": [],
                "retrieved_docs": [],
                "diagnostic_findings": []
            }
            config = {"configurable": {"thread_id": ticket.id}}
            final_state = await asyncio.to_thread(support_graph.invoke, initial_state, config=config)

            # Stream intermediate thoughts from trace
            for step in final_state.get("agent_trace", []):
                yield f"data: {json.dumps({'event': 'trace_step', 'step': step})}\n\n"
                await asyncio.sleep(0.2)

            reply = final_state.get("messages", [])[-1].content
            # Stream tokens
            words = reply.split(" ")
            for w in words:
                yield f"data: {json.dumps({'event': 'token', 'token': w + ' '})}\n\n"
                await asyncio.sleep(0.03)

            yield f"data: {json.dumps({'event': 'done', 'reply': reply, 'trace': final_state.get('agent_trace', [])})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
