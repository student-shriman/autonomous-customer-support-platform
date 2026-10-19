"""
Escalation Agent.
Intercepts high-risk tasks, generates structured incident context packages,
and registers cases into the Human-in-the-Loop review queue.
"""

from typing import Dict, Any, List
from datetime import datetime
from backend.app.agent_core.state import GraphState, AgentTraceStep

def escalation_agent(state: GraphState) -> Dict[str, Any]:
    ticket_id = state.get("ticket_id", "TK-UNKNOWN")
    proposed_action = state.get("proposed_action") or {}
    diagnostic_findings = state.get("diagnostic_findings", [])
    action_risk_level = state.get("action_risk_level", "HIGH")
    intent = state.get("intent", "Customer support escalation")

    incident_package = {
        "ticket_id": ticket_id,
        "intent": intent,
        "escalation_reason": proposed_action.get("reason", "Action requires human authorization"),
        "proposed_action": proposed_action,
        "diagnostic_context": diagnostic_findings,
        "escalated_at": datetime.utcnow().isoformat() + "Z"
    }

    trace_step: AgentTraceStep = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent_name": "Escalation Agent",
        "action_type": "hitl_incident_packaging",
        "summary": f"Packaged high-risk action '{proposed_action.get('type')}' into HITL queue.",
        "details": incident_package
    }

    current_trace = state.get("agent_trace", []).copy()
    current_trace.append(trace_step)

    return {
        "hitl_status": "PENDING",
        "agent_trace": current_trace
    }
