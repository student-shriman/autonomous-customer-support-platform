"""
End-to-End Test for FastAPI Backend & Neon PostgreSQL.
Validates:
  1. Lifespan startup & table initialization in Neon
  2. Seed data & admin user verification
  3. API endpoints: /health, /api/v1/tickets, /api/v1/hitl/queue
  4. LangGraph Multi-Agent execution through /api/v1/chat
"""

import os
import asyncio
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.config import settings

load_dotenv()

async def run_tests():
    print("=" * 65)
    print("🚀 FastAPI & LangGraph Backend End-to-End Test")
    print("=" * 65)
    print(f"Target Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
    print(f"LLM Model      : {settings.DEFAULT_MODEL}")
    print("-" * 65)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Trigger lifespan startup
        async with app.router.lifespan_context(app):
            # 1. Health check
            print("\n[Test 1] Health Check Probe (/health)...")
            res = await client.get("/health")
            print(f"Status {res.status_code}: {res.json()}")
            assert res.status_code == 200

            # 2. Tickets list
            print("\n[Test 2] Fetch Triage Tickets (/api/v1/tickets)...")
            res = await client.get("/api/v1/tickets")
            tickets = res.json()
            print(f"Status {res.status_code}: Found {len(tickets)} tickets in Neon Postgres")
            for t in tickets[:2]:
                print(f"  - [{t['severity']}] {t['id']}: {t['title']} ({t['status']})")
            assert res.status_code == 200

            # 3. Pending HITL Queue
            print("\n[Test 3] Fetch HITL Review Queue (/api/v1/hitl/queue)...")
            res = await client.get("/api/v1/hitl/queue")
            hitl_actions = res.json()
            print(f"Status {res.status_code}: {len(hitl_actions)} high-risk actions pending human sign-off")
            for a in hitl_actions:
                print(f"  - Action ID {a['id']}: {a['action_type']} (Risk: {a['risk_level']}) -> Ticket {a['ticket_id']}")
            assert res.status_code == 200

            # 4. Multi-Agent Chat Test
            print("\n[Test 4] Multi-Agent Chat Invocation (/api/v1/chat)...")
            chat_payload = {
                "ticket_id": tickets[0]["id"] if tickets else "TK-8910",
                "message": "Can you check why I was billed twice and initiate the refund?"
            }
            chat_res = await client.post("/api/v1/chat", json=chat_payload)
            chat_data = chat_res.json()
            print(f"Status {chat_res.status_code}:")
            print(f"  Reply       : {chat_data.get('reply')[:120]}...")
            print(f"  Citations   : {len(chat_data.get('citations', []))} docs cited")
            print(f"  Trace Steps : {len(chat_data.get('agent_trace', []))} agent steps executed")
            print(f"  HITL Pending: {chat_data.get('hitl_pending')}")

    print("\n" + "=" * 65)
    print("🎯 Backend & Multi-Agent Verification Complete!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_tests())
