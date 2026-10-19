from typing import Annotated, Literal, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentTraceStep(TypedDict):
    timestamp: str
    agent_name: str
    action_type: str
    summary: str
    details: Dict[str, Any]

class GraphState(TypedDict):
    # Conversational History
    messages: Annotated[List[BaseMessage], add_messages]
    ticket_id: str
    customer_id: str
    
    # Classification & Context
    intent: str
    severity: Literal["P0", "P1", "P2", "P3"]
    customer_profile: Optional[Dict[str, Any]]
    
    # Investigation & Retrieval
    retrieved_docs: List[Dict[str, Any]]
    diagnostic_findings: List[Dict[str, Any]]
    
    # Resolution & Planning
    proposed_plan: Optional[str]
    proposed_action: Optional[Dict[str, Any]]
    action_risk_level: Literal["LOW", "HIGH"]
    
    # Human-in-the-Loop (HITL) State
    hitl_action_id: Optional[str]
    hitl_status: Optional[Literal["PENDING", "APPROVED", "MODIFIED", "REJECTED"]]
    hitl_review_notes: Optional[str]
    human_modified_action: Optional[Dict[str, Any]]
    
    # Execution Output
    action_execution_result: Optional[Dict[str, Any]]
    resolution_summary: Optional[str]
    agent_trace: List[AgentTraceStep]
    next_node: str
