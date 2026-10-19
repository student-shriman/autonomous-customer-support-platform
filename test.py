"""
Test script for Euri LLM API with gpt-6-luna model.
Demonstrates:
  1. Direct Chat Completion (Basic Call)
  2. Structured JSON Output (Customer Support Triage: Intent & Severity)
  3. Real-Time Streaming (Token-by-token generation for Support Chat)
"""

import os
import sys
import time
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# 1. Load environment variables
load_dotenv()

api_key = os.getenv("EURI_API_KEY")
base_url = os.getenv("EURI_BASE_URL", "https://api.euron.one/api/v1/euri")
model_name = os.getenv("DEFAULT_MODEL", "gpt-6-luna")

print("=" * 60)
print("🚀 EURI LLM API Test (Model: %s)" % model_name)
print("=" * 60)
print(f"Base URL : {base_url}")
print(f"API Key  : {api_key[:8]}...{api_key[-4:] if api_key else 'NONE'}")
print("-" * 60)

if not api_key:
    print("❌ Error: EURI_API_KEY is not set in .env")
    sys.exit(1)

# Initialize LangChain ChatOpenAI client pointing to Euri endpoint
llm = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0.1,
    max_tokens=500,
)

# ----------------------------------------------------------------------
# Test 1: Basic Chat Completion
# ----------------------------------------------------------------------
print("\n[Test 1] Basic Chat Completion Test...")
t0 = time.perf_counter()
try:
    messages = [
        SystemMessage(content="You are the Support Supervisor Agent for an enterprise platform. Be concise and professional."),
        HumanMessage(content="Hello! Can you state your role and confirmation of system readiness?")
    ]
    response = llm.invoke(messages)
    elapsed = time.perf_counter() - t0
    print(f"✅ Response received in {elapsed:.2f}s:")
    print(f"   {response.content.strip()}\n")
except Exception as e:
    print(f"❌ Test 1 failed: {e}\n")

# ----------------------------------------------------------------------
# Test 2: Structured Output (Customer Intent & Severity Classification)
# ----------------------------------------------------------------------
print("[Test 2] Structured Output (Customer Support Triage)...")
class TicketTriage(BaseModel):
    category: str = Field(description="Issue category e.g., Billing, Technical, Account, Feature")
    severity: str = Field(description="Severity level: P0 (Outage), P1 (Financial/Critical), P2 (Feature/Standard), P3 (Minor)")
    intent: str = Field(description="Core customer intent summarized in one sentence")
    requires_human_approval: bool = Field(description="True if financial mutation, refund, or high-risk action is requested")

try:
    t0 = time.perf_counter()
    structured_llm = llm.with_structured_output(TicketTriage)
    sample_customer_query = (
        "I was charged $89 twice for my enterprise tier subscription renewal this morning on invoice #INV-9821. "
        "Please reverse the duplicate charge immediately!"
    )
    triage_result = structured_llm.invoke(
        f"Analyze this customer ticket query and classify it:\n\n\"{sample_customer_query}\""
    )
    elapsed = time.perf_counter() - t0
    print(f"✅ Structured extraction completed in {elapsed:.2f}s:")
    print(f"   Category         : {triage_result.category}")
    print(f"   Severity         : {triage_result.severity}")
    print(f"   Intent           : {triage_result.intent}")
    print(f"   HITL Required    : {triage_result.requires_human_approval}\n")
except Exception as e:
    print(f"❌ Test 2 failed: {e}\n")

# ----------------------------------------------------------------------
# Test 3: Real-Time Streaming Test
# ----------------------------------------------------------------------
print("[Test 3] Real-Time Streaming Test...")
try:
    t0 = time.perf_counter()
    stream_messages = [
        SystemMessage(content="You are a helpful customer support agent. Provide a friendly 2-sentence response explaining how duplicate charges are verified and refunded."),
        HumanMessage(content="How do you handle duplicate charges?")
    ]
    print("   Streaming tokens: ", end="", flush=True)
    first_token_time = None
    token_count = 0
    for chunk in llm.stream(stream_messages):
        if first_token_time is None:
            first_token_time = time.perf_counter() - t0
        content = chunk.content
        if content:
            print(content, end="", flush=True)
            token_count += 1
    total_time = time.perf_counter() - t0
    print(f"\n✅ Streaming finished: TTFT={first_token_time:.2f}s, Total={total_time:.2f}s, Chunks={token_count}\n")
except Exception as e:
    print(f"❌ Test 3 failed: {e}\n")

print("=" * 60)
print("🎯 Euri API & gpt-6-luna Integration Verification Complete!")
print("=" * 60)
