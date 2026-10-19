"""
Knowledge / RAG Agent.
Executes hybrid retrieval (Pinecone + BM25), reranks via gpt-6-luna,
and provides grounded context with citations.
"""

from typing import Dict, Any, List
from datetime import datetime
from backend.app.agent_core.state import GraphState, AgentTraceStep
from backend.app.agent_core.rag.retriever import retriever
from backend.app.agent_core.rag.reranker import reranker

def knowledge_agent(state: GraphState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    user_query = messages[-1].content if messages else "Customer support inquiry"
    intent = state.get("intent", user_query)

    search_query = f"{intent} {user_query}"[:200]

    # 1. Retrieve candidates via Hybrid Retriever
    candidates = retriever.retrieve(search_query, top_k=5)

    # 2. Rerank candidates using gpt-6-luna
    ranked_docs = reranker.rerank(user_query, candidates, top_n=3)

    trace_step: AgentTraceStep = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent_name": "Knowledge / RAG Agent",
        "action_type": "hybrid_search_and_rerank",
        "summary": f"Retrieved {len(candidates)} candidates, reranked to top {len(ranked_docs)} grounding chunks.",
        "details": {
            "search_query": search_query,
            "top_docs": [{"id": d["id"], "title": d["title"], "score": d.get("rerank_score")} for d in ranked_docs]
        }
    }

    current_trace = state.get("agent_trace", []).copy()
    current_trace.append(trace_step)

    return {
        "retrieved_docs": ranked_docs,
        "agent_trace": current_trace
    }
