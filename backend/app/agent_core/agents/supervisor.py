"""
Support Supervisor Agent.
Acts as the central state router and orchestrator:
  - Parses incoming customer query
  - Classifies severity: P0 (Outage), P1 (Billing/Financial), P2 (Feature/Tech), P3 (General)
  - Evaluates current resolution phase and routes dynamically
"""

from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.app.core.config import settings
from backend.app.agent_core.state import GraphState, AgentTraceStep

class SupervisorDecision(BaseModel):
    intent: str = Field(description="Primary intent summary in 1 sentence")
    severity: str = Field(description="Severity: P0, P1, P2, or P3")
    next_step: str = Field(description="Next agent to invoke: 'knowledge', 'troubleshooting', 'resolution', 'clarify', or 'escalate'")
    reasoning: str = Field(description="Brief justification for this routing decision")

def supervisor_agent(state: GraphState) -> Dict[str, Any]:
    llm = ChatOpenAI(
        model=settings.DEFAULT_MODEL,
        api_key=settings.EURI_API_KEY,
        base_url=settings.EURI_BASE_URL,
        temperature=0.1,
        max_tokens=400
    )
    structured_llm = llm.with_structured_output(SupervisorDecision)

    # Get latest user message
    messages = state.get("messages", [])
    user_query = messages[-1].content if messages else "No query provided"
    retrieved_docs = state.get("retrieved_docs", [])
    diagnostic_findings = state.get("diagnostic_findings", [])
    proposed_plan = state.get("proposed_plan")

    prompt = (
        f"You are the Support Supervisor Agent for an enterprise customer support platform.\n"
        f"Customer Query: \"{user_query}\"\n"
        f"Current State:\n"
        f"- Retrieved Docs Count: {len(retrieved_docs)}\n"
        f"- Diagnostic Findings Count: {len(diagnostic_findings)}\n"
        f"- Has Proposed Plan: {bool(proposed_plan)}\n\n"
        f"Rules:\n"
        f"1. If this is a billing dispute, unexpected charge, or technical glitch and diagnostics haven't run, route to 'troubleshooting'.\n"
        f"2. If policy, documentation, or knowledge is required and docs haven't been retrieved, route to 'knowledge'.\n"
        f"3. If both diagnostics/context and knowledge have been gathered, route to 'resolution'.\n"
        f"4. If query is vague, route to 'clarify'.\n"
        f"5. If catastrophic outage is detected, route to 'escalate'."
    )

    try:
        decision: SupervisorDecision = structured_llm.invoke(prompt)
    except Exception as e:
        decision = SupervisorDecision(
            intent="Customer support request",
            severity="P2",
            next_step="troubleshooting" if not diagnostic_findings else "resolution",
            reasoning=f"Default routing fallback: {e}"
        )

    trace_step: AgentTraceStep = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent_name": "Supervisor Agent",
        "action_type": "intent_and_severity_routing",
        "summary": f"Classified {decision.severity} ({decision.intent}) -> Route to '{decision.next_step}'",
        "details": {
            "intent": decision.intent,
            "severity": decision.severity,
            "next_step": decision.next_step,
            "reasoning": decision.reasoning
        }
    }

    current_trace = state.get("agent_trace", []).copy()
    current_trace.append(trace_step)

    return {
        "intent": decision.intent,
        "severity": decision.severity,
        "next_node": decision.next_step,
        "agent_trace": current_trace
    }
