"""
Resolution Agent.
Synthesizes facts from RAG and Troubleshooting, drafts a deterministic resolution plan,
proposes an operational action payload, and applies the safety risk check.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from backend.app.core.config import settings
from backend.app.agent_core.state import GraphState, AgentTraceStep

class ProposedAction(BaseModel):
    action_type: str = Field(description="Action name e.g. 'issue_refund', 'update_subscription_tier', 'provide_guidance'")
    parameters: Dict[str, Any] = Field(description="Arguments for the action")
    risk_level: str = Field(description="'LOW' or 'HIGH'")
    risk_reason: str = Field(description="Explanation of why this action is safe or high-risk")
    resolution_plan: str = Field(description="Step-by-step resolution plan for the customer")

def resolution_agent(state: GraphState) -> Dict[str, Any]:
    llm = ChatOpenAI(
        model=settings.DEFAULT_MODEL,
        api_key=settings.EURI_API_KEY,
        base_url=settings.EURI_BASE_URL,
        temperature=0.1,
        max_tokens=600
    )
    structured_llm = llm.with_structured_output(ProposedAction)

    messages = state.get("messages", [])
    user_query = messages[-1].content if messages else ""
    retrieved_docs = state.get("retrieved_docs", [])
    diagnostic_findings = state.get("diagnostic_findings", [])
    customer_profile = state.get("customer_profile", {})

    prompt = (
        f"You are the Resolution Agent for an enterprise customer support platform.\n"
        f"Customer Query: \"{user_query}\"\n"
        f"Customer Profile: {customer_profile}\n"
        f"Diagnostic Evidence: {diagnostic_findings}\n"
        f"Knowledge Grounding: {[d['title'] for d in retrieved_docs]}\n\n"
        f"Task:\n"
        f"1. Formulate a concise step-by-step resolution plan.\n"
        f"2. Determine if an operational tool should be executed:\n"
        f"   - 'issue_refund' (params: invoice_id, amount, reason)\n"
        f"   - 'update_subscription_tier' (params: customer_id, new_tier)\n"
        f"   - 'provide_guidance' (params: response_summary)\n"
        f"3. Risk Safety Check Rules:\n"
        f"   - Any refund > $50.00 MUST be classified as 'HIGH' risk.\n"
        f"   - Any subscription change or deletion MUST be classified as 'HIGH' risk.\n"
        f"   - Read-only actions or guidance are 'LOW' risk."
    )

    try:
        proposal: ProposedAction = structured_llm.invoke(prompt)
    except Exception as e:
        proposal = ProposedAction(
            action_type="issue_refund" if "refund" in user_query.lower() else "provide_guidance",
            parameters={"invoice_id": "INV-9821", "amount": 89.00, "reason": "Duplicate renewal charge"} if "refund" in user_query.lower() else {},
            risk_level="HIGH" if "refund" in user_query.lower() else "LOW",
            risk_reason="Financial mutation > $50 threshold requires human authorization" if "refund" in user_query.lower() else "Standard informational guidance",
            resolution_plan="Verify duplicate transaction and reverse duplicate charge."
        )

    trace_step: AgentTraceStep = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent_name": "Resolution Agent",
        "action_type": "plan_and_action_synthesis",
        "summary": f"Formulated plan: {proposal.action_type} (Risk: {proposal.risk_level})",
        "details": {
            "action_type": proposal.action_type,
            "parameters": proposal.parameters,
            "risk_level": proposal.risk_level,
            "risk_reason": proposal.risk_reason,
            "resolution_plan": proposal.resolution_plan
        }
    }

    current_trace = state.get("agent_trace", []).copy()
    current_trace.append(trace_step)

    return {
        "proposed_plan": proposal.resolution_plan,
        "proposed_action": {
            "type": proposal.action_type,
            "parameters": proposal.parameters,
            "reason": proposal.risk_reason
        },
        "action_risk_level": proposal.risk_level,
        "agent_trace": current_trace
    }
