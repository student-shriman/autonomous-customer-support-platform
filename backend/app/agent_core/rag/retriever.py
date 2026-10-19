"""
Hybrid RAG Retriever combining:
  1. Pinecone Vector Search (Semantic Dense Search via text-embedding-3-small)
  2. In-Memory BM25 / Keyword Retrieval (Exact Keyword & Lexical Matching)
"""

import os
import re
from typing import List, Dict, Any
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from backend.app.core.config import settings

# Built-in enterprise documentation corpus for fallback & hybrid lexical search
_KNOWLEDGE_DOCS = [
    {
        "id": "kb-billing-refund-001",
        "title": "Duplicate Charge & Refund Policy (KB-401)",
        "category": "Billing",
        "text": (
            "Billing Policy KB-401: Duplicate subscription renewals are eligible for an immediate full refund "
            "to the original payment method if reported within 30 days. Standard turnaround is 1-3 business days. "
            "Refunds over $50 require Tier 2 or Human Specialist approval."
        )
    },
    {
        "id": "kb-tech-rate-limit-002",
        "title": "API Rate Limits & 429 Errors (KB-205)",
        "category": "Technical",
        "text": (
            "API Troubleshooting KB-205: Standard tier allows 60 req/min. Enterprise tier supports up to 1200 req/min. "
            "When encountering HTTP 429 Too Many Requests, implement exponential backoff with jitter. "
            "Quota upgrades take effect within 5 minutes."
        )
    },
    {
        "id": "kb-account-sso-003",
        "title": "SAML 2.0 & Google Workspace SSO Configuration (KB-310)",
        "category": "Account",
        "text": (
            "Authentication Guide KB-310: Enterprise accounts can enable SAML 2.0 via Okta, Azure AD, or Google Workspace. "
            "ACS URL and Entity ID are available in Dashboard > Security > Single Sign-On."
        )
    },
    {
        "id": "kb-ops-maintenance-004",
        "title": "Scheduled Maintenance & Outage Protocol (KB-101)",
        "category": "Operations",
        "text": (
            "System Outages KB-101: P0 Critical incidents (database partition, cluster downtime) trigger automated "
            "pager escalation to on-call SRE. Real-time status updates are posted at status.cloudscale.io."
        )
    }
]

class HybridRetriever:
    def __init__(self):
        self.pc = None
        self.index = None
        self.embeddings = None
        
        if settings.PINECONE_API_KEY and settings.PINECONE_HOST:
            try:
                self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                self.index = self.pc.Index(
                    name=settings.PINECONE_INDEX_NAME,
                    host=settings.PINECONE_HOST
                )
            except Exception as e:
                print(f"[HybridRetriever] Pinecone initialization warning: {e}")

        if settings.EURI_API_KEY:
            try:
                self.embeddings = OpenAIEmbeddings(
                    model=settings.EMBEDDING_MODEL,
                    api_key=settings.EURI_API_KEY,
                    base_url=settings.EURI_BASE_URL,
                    check_embedding_ctx_length=False
                )
            except Exception as e:
                print(f"[HybridRetriever] Embeddings initialization warning: {e}")

    def _lexical_score(self, query: str, doc_text: str) -> float:
        """Simple BM25-style lexical keyword overlap score."""
        tokens = set(re.findall(r"\w+", query.lower()))
        if not tokens:
            return 0.0
        doc_tokens = re.findall(r"\w+", doc_text.lower())
        overlap = sum(1 for t in doc_tokens if t in tokens)
        return overlap / (len(doc_tokens) + 10.0)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform hybrid retrieval over Pinecone vector index and local knowledge docs."""
        candidates = {}

        # 1. Pinecone Vector Search
        if self.index and self.embeddings:
            try:
                q_vec = self.embeddings.embed_query(query)
                res = self.index.query(
                    vector=q_vec,
                    top_k=top_k,
                    include_metadata=True,
                    namespace="kb-docs"
                )
                for match in res.matches:
                    meta = match.metadata or {}
                    candidates[match.id] = {
                        "id": match.id,
                        "title": meta.get("title", match.id),
                        "text": meta.get("text", ""),
                        "category": meta.get("category", "General"),
                        "dense_score": float(match.score),
                        "sparse_score": self._lexical_score(query, meta.get("text", ""))
                    }
            except Exception as e:
                print(f"[HybridRetriever] Pinecone query error: {e}")

        # 2. Lexical Fallback / Augmentation
        for doc in _KNOWLEDGE_DOCS:
            if doc["id"] not in candidates:
                sparse_score = self._lexical_score(query, doc["text"])
                if sparse_score > 0.05:
                    candidates[doc["id"]] = {
                        "id": doc["id"],
                        "title": doc["title"],
                        "text": doc["text"],
                        "category": doc["category"],
                        "dense_score": 0.0,
                        "sparse_score": sparse_score
                    }

        # Combine into candidate list
        results = list(candidates.values())
        # Sort by composite score
        results.sort(key=lambda d: (d["dense_score"] * 0.7) + (d["sparse_score"] * 0.3), reverse=True)
        return results[:top_k]

retriever = HybridRetriever()
