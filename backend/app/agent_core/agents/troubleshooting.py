"""
Troubleshooting Agent.
Formulates diagnostic hypotheses, inspects account state, checks transaction logs,
and identifies root causes via MCP tools.
"""

from typing import Dict, Any, List
from datetime import datetime
from backend.app.agent_core.state import GraphState, AgentTraceStep
from backend.app.agent_core.tools.mcp_tools import (
    get_customer_profile,
    get_invoices_and_charges,
    inspect_diagnostic_logs
)

def troubleshooting_agent(state: GraphState) -> Dict[str, Any]:
    customer_id = state.get("customer_id", "cust_default")
    intent = state.get("intent", "").lower()
    messages = state.get("messages", [])
    last_msg = messages[-1].content.lower() if messages else ""

    findings = []
    
    # 1. Fetch Customer Profile
    prof_res = get_customer_profile(customer_id)
    profile = prof_res.get("profile", {})
    findings.append({
        "type": "account_profile",
        "details": f"Customer: {profile.get('name')} | Tier: {profile.get('tier')} | Status: {profile.get('status')}"
    })

    # 2. Check Billing if related to charge/invoice/refund
    if any(k in intent or k in last_msg for k in ["charge", "refund", "invoice", "bill", "duplicate", "payment", "$"]):
        inv_res = get_invoices_and_charges(customer_id, limit=3)
        invoices = inv_res.get("invoices", [])
        
        # Check for duplicates
        amounts = [inv["amount"] for inv in invoices]
        has_dup = len(amounts) != len(set(amounts))
        
        findings.append({
            "type": "billing_investigation",
            "invoices_found": len(invoices),
            "recent_invoices": invoices,
            "duplicate_detected": has_dup,
            "summary": f"Detected potential duplicate charges for amount ${invoices[0]['amount'] if invoices else 0.0}" if has_dup else "No duplicate charge found in recent 3 invoices."
        })

    # 3. Check System Telemetry / Error logs
    log_res = inspect_diagnostic_logs(service="billing" if "bill" in intent else "api-gateway")
    logs = log_res.get("logs", [])
    warn_logs = [l for l in logs if l.get("level") in ("WARN", "ERROR")]
    if warn_logs:
        findings.append({
            "type": "telemetry_logs",
            "warning_count": len(warn_logs),
            "evidence": warn_logs[0].get("message")
        })

    trace_step: AgentTraceStep = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent_name": "Troubleshooting Agent",
        "action_type": "diagnostic_investigation",
        "summary": f"Ran diagnostic tools: {len(findings)} findings gathered across account and transaction telemetry.",
        "details": {
            "findings": findings
        }
    }

    current_trace = state.get("agent_trace", []).copy()
    current_trace.append(trace_step)

    return {
        "customer_profile": profile,
        "diagnostic_findings": findings,
        "agent_trace": current_trace
    }
