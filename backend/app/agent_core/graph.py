"""
LangGraph Multi-Agent Cyclical State Machine.
Orchestrates:
  - Supervisor Agent
  - Customer Agent
  - Knowledge / RAG Agent
  - Troubleshooting Agent
  - Resolution Agent
  - Escalation Agent
  - Action Executor (MCP Tools)
"""

from typing import Dict, Any, Literal
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.app.agent_core.state import GraphState, AgentTraceStep
from backend.app.agent_core.agents.supervisor import supervisor_agent
from backend.app.agent_core.agents.customer import customer_agent
from backend.app.agent_core.agents.knowledge import knowledge_agent
from backend.app.agent_core.agents.troubleshooting import troubleshooting_agent
from backend.app.agent_core.agents.resolution import resolution_agent
from backend.app.agent_core.agents.escalation import escalation_agent
from backend.app.agent_core.tools.mcp_tools import issue_refund, update_subscription_tier

def action_executor_node(state: GraphState) -> Dict[str, Any]:
    """Execute approved operational tool calls via MCP."""
    proposed = state.get("proposed_action") or {}
    act_type = proposed.get("type", "")
    params = proposed.get("parameters", {})
    
    # If human modified the action payload in HITL
    if state.get("human_modified_action"):
        params = state.get("human_modified_action")

    result = {}
    if act_type == "issue_refund":
        result = issue_refund(
            invoice_id=params.get("invoice_id", "INV-UNKNOWN"),
            amount=float(params.get("amount", 0.0)),
            reason=params.get("reason", "Approved support refund")
        )
    elif act_type == "update_subscription_tier":
        result = update_subscription_tier(
            customer_id=params.get("customer_id", state.get("customer_id", "cust_default")),
            new_tier=params.get("new_tier", "starter")
        )
    else:
        result = {"status": "completed", "action": "informational_resolution", "details": params}

    trace_step: AgentTraceStep = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent_name": "Action Executor Engine",
        "action_type": "mcp_tool_execution",
        "summary": f"Executed MCP operational tool: {act_type}",
        "details": result
    }

    current_trace = state.get("agent_trace", []).copy()
    current_trace.append(trace_step)

    return {
        "action_execution_result": result,
        "agent_trace": current_trace
    }

# Conditional routing functions
def route_from_supervisor(state: GraphState) -> str:
    next_node = state.get("next_node", "knowledge")
    if next_node in ("knowledge", "troubleshooting", "resolution", "escalate"):
        return next_node
    return "customer"

def route_from_resolution(state: GraphState) -> str:
    risk = state.get("action_risk_level", "LOW")
    if risk == "HIGH":
        return "escalation"
    return "action_executor"

def build_support_graph():
    """Build and compile the multi-agent state graph."""
    workflow = StateGraph(GraphState)

    # 1. Add all nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("troubleshooting", troubleshooting_agent)
    workflow.add_node("knowledge", knowledge_agent)
    workflow.add_node("resolution", resolution_agent)
    workflow.add_node("action_executor", action_executor_node)
    workflow.add_node("escalation", escalation_agent)
    workflow.add_node("customer", customer_agent)

    # 2. Add edges
    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "troubleshooting": "troubleshooting",
            "knowledge": "knowledge",
            "resolution": "resolution",
            "escalate": "escalation",
            "customer": "customer"
        }
    )

    # Sub-agent loops
    workflow.add_edge("troubleshooting", "knowledge")
    workflow.add_edge("knowledge", "resolution")

    # Resolution branch
    workflow.add_conditional_edges(
        "resolution",
        route_from_resolution,
        {
            "action_executor": "action_executor",
            "escalation": "escalation"
        }
    )

    workflow.add_edge("action_executor", "customer")
    workflow.add_edge("escalation", "customer")
    workflow.add_edge("customer", END)

    # Memory Checkpointer
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    return app

support_graph = build_support_graph()
