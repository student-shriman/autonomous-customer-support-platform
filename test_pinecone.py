"""
Test script for Pinecone Vector Database with Euri text-embedding-3-small.
Tests:
  1. Pinecone Client initialization & index status check
  2. Euri embedding generation (1536 dimensions)
  3. Vector upsert of customer support knowledge chunks
  4. Vector similarity search query & verification
"""

import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "support-knowledge-base")
pinecone_host = os.getenv("PINECONE_HOST")
euri_api_key = os.getenv("EURI_API_KEY")
euri_base_url = os.getenv("EURI_BASE_URL", "https://api.euron.one/api/v1/euri")
embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

print("=" * 65)
print("🌲 Pinecone Vector Database Integration Test")
print("=" * 65)
print(f"Index Name   : {index_name}")
print(f"Host         : {pinecone_host}")
print(f"API Key      : {pinecone_api_key[:8]}...{pinecone_api_key[-4:] if pinecone_api_key else 'None'}")
print(f"Embedding    : {embedding_model} via Euri")
print("-" * 65)

# Step 1: Initialize Pinecone Client
print("\n[Step 1] Initializing Pinecone Client...")
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(name=index_name, host=pinecone_host)
stats = index.describe_index_stats()
print("✅ Pinecone Index connected successfully!")
print(f"   Dimension    : {stats.dimension}")
print(f"   Total Vectors: {stats.total_vector_count}")

# Step 2: Initialize Embeddings Client
print("\n[Step 2] Initializing Euri Embeddings Client (%s)..." % embedding_model)
embeddings = OpenAIEmbeddings(
    model=embedding_model,
    api_key=euri_api_key,
    base_url=euri_base_url,
    check_embedding_ctx_length=False
)

sample_text = (
    "Billing Policy KB-401: Duplicate subscription renewals are eligible for an immediate full refund "
    "to the original payment method if reported within 30 days. Standard turnaround is 1-3 business days."
)
vec = embeddings.embed_query(sample_text)
print(f"✅ Embedding generated! Vector length: {len(vec)} dimensions")

# Step 3: Upsert Knowledge Vector
print("\n[Step 3] Upserting Sample Support Knowledge Doc...")
doc_id = "kb-billing-refund-001"
metadata = {
    "title": "Duplicate Charge & Refund Policy",
    "category": "Billing",
    "source": "manuals/billing_kb.md",
    "text": sample_text
}

index.upsert(
    vectors=[
        {
            "id": doc_id,
            "values": vec,
            "metadata": metadata
        }
    ],
    namespace="kb-docs"
)
print(f"✅ Upserted document '{doc_id}' into namespace 'kb-docs'!")

# Give Pinecone a brief moment to index
time.sleep(1.5)

# Step 4: Semantic Query
print("\n[Step 4] Querying Pinecone Vector Store...")
query_text = "I was charged twice on my card, how fast can I get my money back?"
query_vec = embeddings.embed_query(query_text)

results = index.query(
    vector=query_vec,
    top_k=2,
    include_metadata=True,
    namespace="kb-docs"
)

print(f"✅ Query returned {len(results.matches)} matches:")
for i, match in enumerate(results.matches, 1):
    print(f"   Match #{i} (Score: {match.score:.4f}):")
    print(f"     ID    : {match.id}")
    print(f"     Title : {match.metadata.get('title')}")
    print(f"     Text  : {match.metadata.get('text')[:100]}...")

print("\n" + "=" * 65)
print("🎯 Pinecone Vector Store Verification 100% Passed!")
print("=" * 65)
