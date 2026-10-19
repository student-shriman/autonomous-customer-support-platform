"""
LLM Reranker powered by gpt-6-luna.
Re-orders retrieved candidate chunks with zero local memory/PyTorch overhead,
perfect for Render deployment.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from backend.app.core.config import settings

class RerankedItem(BaseModel):
    doc_id: str = Field(description="ID of the candidate document")
    relevance_score: float = Field(description="Relevance score from 0.0 to 1.0")
    justification: str = Field(description="Brief explanation of why this document matches the customer request")

class RerankResult(BaseModel):
    ranked_documents: List[RerankedItem]

class LLMReranker:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            api_key=settings.EURI_API_KEY,
            base_url=settings.EURI_BASE_URL,
            temperature=0.0,
            max_tokens=600
        )
        self.structured_llm = self.llm.with_structured_output(RerankResult)

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        """Re-rank candidate documents based on query relevance using gpt-6-luna."""
        if not candidates:
            return []
        
        # If only 1 candidate, return as is
        if len(candidates) == 1:
            candidates[0]["rerank_score"] = 0.95
            candidates[0]["justification"] = "Sole retrieved matching reference"
            return candidates

        # Format candidates for prompt
        doc_summaries = []
        for i, c in enumerate(candidates):
            doc_summaries.append(f"[{i+1}] ID: {c['id']}\nTitle: {c['title']}\nSnippet: {c['text'][:300]}")
        
        prompt = (
            f"You are an expert technical reranker for an enterprise customer support platform.\n"
            f"Customer Query: \"{query}\"\n\n"
            f"Candidate Documents:\n" + "\n\n".join(doc_summaries) + "\n\n"
            f"Score and rank each document by how directly and accurately it answers the customer query. "
            f"Return the top most relevant documents with a relevance_score (0.0 to 1.0) and justification."
        )

        try:
            res: RerankResult = self.structured_llm.invoke(prompt)
            # Create a lookup map for fast retrieval
            cand_map = {c["id"]: c for c in candidates}
            reranked = []
            for item in res.ranked_documents:
                if item.doc_id in cand_map:
                    doc = cand_map[item.doc_id].copy()
                    doc["rerank_score"] = item.relevance_score
                    doc["justification"] = item.justification
                    reranked.append(doc)
            
            # Sort descending by score
            reranked.sort(key=lambda d: d.get("rerank_score", 0.0), reverse=True)
            return reranked[:top_n] if reranked else candidates[:top_n]
        except Exception as e:
            print(f"[LLMReranker] Reranking fallback due to: {e}")
            return candidates[:top_n]

reranker = LLMReranker()
