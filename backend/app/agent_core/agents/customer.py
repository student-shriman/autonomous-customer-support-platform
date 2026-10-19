"""
Customer Agent.
Manages natural language dialogue, empathetic tone, active conversation memory,
and customer-facing response delivery.
"""

from typing import Dict, Any, List
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from backend.app.core.config import settings
from backend.app.agent_core.state import GraphState, AgentTraceStep

def customer_agent(state: GraphState) -> Dict[str, Any]:
    llm = ChatOpenAI(
        model=settings.DEFAULT_MODEL,
        api_key=settings.EURI_API_KEY,
        base_url=settings.EURI_BASE_URL,
        temperature=0.3,
        max_tokens=600
    )

    messages = state.get("messages", [])
    proposed_plan = state.get("proposed_plan")
    action_risk_level = state.get("action_risk_level", "LOW")
    action_execution_result = state.get("action_execution_result")
    hitl_status = state.get("hitl_status")
    retrieved_docs = state.get("retrieved_docs", [])
    customer_profile = state.get("customer_profile") or {}

    customer_name = customer_profile.get("name", "Valued Customer")
    tier = customer_profile.get("tier", "Enterprise")

    # Formulate context for the response
    context_notes = []
    if proposed_plan:
        context_notes.append(f"Resolution Plan: {proposed_plan}")
    if action_execution_result:
        context_notes.append(f"Action Executed: {action_execution_result}")
    if action_risk_level == "HIGH" and hitl_status == "PENDING":
        context_notes.append(
            "Status: A high-risk action (such as a financial refund or account modification) was formulated and queued "
            "for human support specialist review for safety compliance. Inform the customer transparently."
        )
    if retrieved_docs:
        cited = [f"{d['title']}" for d in retrieved_docs[:2]]
        context_notes.append(f"Cited Policies: {', '.join(cited)}")

    system_prompt = (
        f"You are the Customer Support Agent for an enterprise platform. "
        f"You are speaking with {customer_name} ({tier.capitalize()} Tier).\n"
        f"Tone: Empathetic, crisp, highly competent, professional.\n"
        f"Operational Context:\n" + "\n".join(context_notes) + "\n\n"
        f"Draft a helpful, direct response to the customer. "
        f"Do not mention internal technical jargon or agent state names. "
        f"If human approval is pending, reassure them that a specialist is providing immediate sign-off."
    )

    prompt_messages = [SystemMessage(content=system_prompt)]
    # Append recent conversation history
    prompt_messages.extend(messages[-3:] if len(messages) >= 3 else messages)

    try:
        response = llm.invoke(prompt_messages)
        reply_content = response.content
    except Exception as e:
        reply_content = f"Thank you for reaching out. We are reviewing your inquiry and will update you shortly. (Ref: {e})"

    trace_step: AgentTraceStep = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent_name": "Customer Agent",
        "action_type": "customer_response_synthesis",
        "summary": "Generated customer-facing response with tone alignment and citations.",
        "details": {
            "tier": tier,
            "cited_docs_count": len(retrieved_docs),
            "hitl_flag": action_risk_level == "HIGH"
        }
    }

    current_trace = state.get("agent_trace", []).copy()
    current_trace.append(trace_step)

    return {
        "messages": [AIMessage(content=reply_content)],
        "agent_trace": current_trace
    }
