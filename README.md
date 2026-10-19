# Autonomous Customer Support & Resolution Platform

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.4+-000000.svg?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.3+-FF6F00.svg?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Neon Postgres](https://img.shields.io/badge/Neon-PostgreSQL_18.6-00E599.svg?style=for-the-badge&logo=postgresql&logoColor=black)](https://neon.tech)
[![Pinecone](https://img.shields.io/badge/Pinecone-Serverless_Vector_DB-000000.svg?style=for-the-badge&logo=pinecone&logoColor=white)](https://pinecone.io)
[![Clerk SSO](https://img.shields.io/badge/Clerk-Authentication-6C47FF.svg?style=for-the-badge&logo=clerk&logoColor=white)](https://clerk.com)
[![Render](https://img.shields.io/badge/Render-Deployable-46E3B7.svg?style=for-the-badge&logo=render&logoColor=black)](https://render.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<p align="center">
  <strong>Beyond passive bots: An enterprise-grade, autonomous, multi-agent AI customer support platform that investigates root causes, checks system telemetry, executes approved operational actions via MCP, and gates high-risk mutations with human sign-off.</strong>
</p>

[System Architecture](#-system-architecture) •
[Key Capabilities](#-key-capabilities) •
[Agentic Core](#-multi-agent-orchestration-langgraph) •
[Tech Stack](#-technology-stack) •
[Quickstart](#-quickstart--local-setup) •
[API Specs](#-api-endpoints-reference) •
[Render Deployment](#-deploying-on-render)

</div>

---

## 🌟 Executive Summary & Mission

Modern enterprises receive high volumes of customer service requests across fragmented channels: email, real-time chat, and tickets. Standard automated chatbots suffer from a critical limitation: **they are passive, read-only text generators** that cannot investigate system logs, diagnose account errors, or safely execute state-changing actions.

The **Autonomous Customer Support & Resolution Platform** solves this by implementing a stateful, cyclical multi-agent graph capable of:
- **Understanding**: Ambiguous natural language requests, extracting customer intent, and classifying priority/severity (**P0 Outage, P1 Billing, P2 Technical, P3 Minor**).
- **Investigating**: Customer accounts, active subscriptions, and server telemetry logs via **Model Context Protocol (MCP)** tools.
- **Retrieving**: Grounded facts via **Advanced Hybrid RAG** (Pinecone dense vectors + BM25 lexical search) reranked by **`gpt-6-luna`** for zero-overhead accuracy.
- **Deciding & Planning**: Deterministic step-by-step resolution pathways with clear justifications.
- **Acting**: Executing safe operational actions directly via approved API mutations.
- **Escalating**: Pausing high-risk or financial actions (> $50 refund threshold) via a **Human-in-the-Loop (HITL)** approval gate.
- **Remembering & Learning**: Multi-turn short-term conversation context + Neon PostgreSQL long-term ticket history.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Clients["Frontend Client Layer (Next.js 16 + React 19)"]
        ChatPortal["Customer Chat Portal\n(Real-time SSE Streaming)"]
        OpsDashboard["Support Ops Dashboard\n(Triage Feed & Severity Badges)"]
        HITLCenter["HITL Action Review Center\n(Approve / Modify / Reject)"]
        TraceViewer["Visual Agent Trace Viewer\n(Step-by-step Execution Flow)"]
    end

    subgraph Gateway["API & Security Gateway (FastAPI)"]
        Auth["Clerk SSO & RBAC\n(Admin, Agent, Customer)"]
        Guardrails["Security & PII Masking Guardrails"]
        SSEStreamer["SSE Event Streamer"]
        APIRouter["REST Endpoints (/tickets, /chat, /hitl)"]
    end

    subgraph AgentCore["Multi-Agent Layer (LangGraph Cyclical State Machine)"]
        Supervisor["Support Supervisor Agent\n(Router & P0-P3 Classifier)"]
        Troubleshooting["Troubleshooting Agent\n(Telemetry Logs & Diagnoser)"]
        Knowledge["Knowledge / RAG Agent\n(Pinecone + BM25 Hybrid)"]
        Reranker["gpt-6-luna LLM Reranker\n(Listwise Relevance Scoring)"]
        Resolution["Resolution Agent\n(Plan Synthesis & Action Proposal)"]
        Escalation["Escalation Agent\n(HITL Incident Packager)"]
        Executor["Action Executor Engine\n(Operational MCP Tools)"]
        CustomerAgent["Customer Agent\n(Empathetic Response & Tone)"]
    end

    subgraph Storage["Data & Knowledge Stores"]
        NeonDB[("Neon Serverless PostgreSQL 18.6\n(Tickets, Messages, HITL Queue, Audit Trail)")]
        PineconeDB[("Pinecone Serverless Vector Store\n(1536-dim KB Docs & Resolution Pairs)")]
        EuriAPI["Euri LLM Gateway\n(gpt-6-luna & text-embedding-3-small)"]
    end

    ChatPortal <-->|SSE & REST| Gateway
    OpsDashboard <-->|REST| Gateway
    HITLCenter <-->|REST| Gateway
    TraceViewer <-->|REST| Gateway

    Gateway <--> AgentCore
    AgentCore <--> Storage
```

---

## 🤖 Multi-Agent Orchestration (LangGraph)

The agentic layer is structured as a stateful cyclical directed graph in **LangGraph**:

| Agent | Responsibility | Core Tools & Actions |
| :--- | :--- | :--- |
| **1. Support Supervisor** | Central router and orchestrator. Classifies ticket severity (P0–P3) and routes dynamically based on missing context. | State machine router, intent extraction, Pydantic classification. |
| **2. Customer Agent** | Formulates empathetic, customer-facing messages adhering to customer tier (VIP Enterprise handling). | Dialogue memory, tone alignment, citation injector. |
| **3. Knowledge / RAG Agent** | Hybrid retrieval combining dense vector similarity and sparse BM25 keyword matching. | Pinecone index, `text-embedding-3-small`, candidate retrieval. |
| **4. `gpt-6-luna` Reranker** | Re-orders candidate documents with structured listwise scoring and relevance justifications. | Zero-memory LLM reranker, noise filter. |
| **5. Troubleshooting Agent** | Inspects account subscriptions, checks recent invoices for duplicate transactions, and parses telemetry error logs. | `get_customer_profile`, `get_invoices_and_charges`, `inspect_diagnostic_logs`. |
| **6. Resolution Agent** | Synthesizes findings, builds deterministic resolution plans, and applies safety checks. | Operational action proposer, risk scoring ($50 financial limit). |
| **7. Escalation Agent** | Intercepts high-risk tasks and packages incident payloads into the human review queue. | Incident packager, HITL queue publisher. |

---

## 🛡️ Human-in-the-Loop (HITL) Safety Gate

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Customer
    participant Agent as LangGraph Core
    participant DB as Neon PostgreSQL
    actor Specialist as Human Support Specialist
    participant MCP as MCP Operational Tools

    Customer->>Agent: Request refund for duplicate invoice charge
    Agent->>Agent: Supervisor routes to Troubleshooting and Knowledge
    Agent->>Agent: Troubleshooting confirms duplicate charge
    Agent->>Agent: Resolution Agent drafts refund action
    Agent->>Agent: Risk check: Financial action exceeds 50 dollar limit
    Agent->>DB: Save checkpoint and register action in hitl_actions
    Agent-->>Customer: Refund drafted, awaiting specialist sign-off
    DB-->>Specialist: Action displayed in HITL Review Center
    alt Approve Action
        Specialist->>Agent: Submit Decision: APPROVED
        Agent->>MCP: Execute issue_refund tool
        MCP-->>Agent: Refund confirmation returned
        Agent-->>Customer: Refund of 89 dollars processed successfully
    else Modify Action
        Specialist->>Agent: Submit Decision: MODIFIED (Adjust amount)
        Agent->>MCP: Execute issue_refund with updated amount
    else Reject Action
        Specialist->>Agent: Submit Decision: REJECTED
        Agent-->>Customer: Request reviewed, refund declined per policy
    end
```

---

## 🛠️ Technology Stack

| Layer | Technology | Production Justification |
| :--- | :--- | :--- |
| **Frontend UI** | **Next.js 16 (App Router)** + **React 19** + **Tailwind CSS** | Server-side rendering, Turbopack, responsive dashboard, Lucide icons. |
| **Auth & SSO** | **Clerk SSO** + Local JWT Fallback | Modern enterprise identity, social logins, role-based access control. |
| **Backend API** | **FastAPI (Python 3.12)** + **Uvicorn** | High-performance asynchronous REST and real-time SSE streaming. |
| **Orchestration** | **LangGraph 0.3+** + **LangChain 0.3+** | Stateful cyclical graphs with conditional routing and checkpoint breakpoints. |
| **Foundation Model** | **`gpt-6-luna`** (via Euri Gateway) | High-speed, high-reasoning LLM for routing, synthesis, and structured reranking. |
| **Embeddings** | **`text-embedding-3-small`** (1536 dim) | Industry-standard semantic representations for technical documentation. |
| **Relational DB** | **Neon Serverless PostgreSQL 18.6** | Serverless relational store with `psycopg 3` and `asyncpg` drivers. |
| **Vector DB** | **Pinecone Serverless** (`support-knowledge-base`) | Managed cosine-similarity vector store for Hybrid RAG grounding. |
| **Operational Tools** | **Model Context Protocol (MCP)** | Decoupled tool schemas for billing, accounts, and telemetry logs. |
| **Deployment** | **Render** (`render.yaml`) | Multi-service cloud deployment with automated zero-downtime builds. |

---

## 📁 Repository Directory Layout

```
autonomous_customer_support_platform/
├── backend/
│   ├── app/
│   │   ├── agent_core/
│   │   │   ├── agents/            # 6 specialized LangGraph agent nodes
│   │   │   │   ├── supervisor.py  # Intent & severity router
│   │   │   │   ├── customer.py    # Conversational tone & persona
│   │   │   │   ├── knowledge.py   # Hybrid search retriever
│   │   │   │   ├── troubleshooting.py # Telemetry logs & diagnostics
│   │   │   │   ├── resolution.py  # Plan synthesis & risk gate
│   │   │   │   └── escalation.py  # HITL incident packager
│   │   │   ├── rag/               # Hybrid retriever & gpt-6-luna reranker
│   │   │   ├── tools/             # MCP operational tools (CRM, Billing, Logs)
│   │   │   ├── graph.py           # LangGraph StateGraph builder
│   │   │   └── state.py           # GraphState TypedDict definition
│   │   ├── api/                   # REST & SSE streaming routers
│   │   ├── core/                  # Database, Security (bcrypt & JWT), Config
│   │   ├── models/                # Neon PostgreSQL SQLAlchemy models
│   │   ├── schemas/               # Pydantic validation schemas
│   │   ├── services/              # Guardrails, Seed Data, Ticket services
│   │   └── main.py                # FastAPI entrypoint
│   └── Dockerfile                 # Multi-stage Python production Dockerfile
│
├── frontend/                      # Next.js 16 Support Portal
│   ├── app/                       # App Router (layout, page, globals)
│   ├── components/                # React Components
│   │   ├── Navbar.tsx             # Brand navigation & Admin badge
│   │   ├── DashboardView.tsx      # Support Ops Center & Triage feed
│   │   ├── HITLActionCenter.tsx   # Human review queue & controls
│   │   ├── CustomerPortalView.tsx # Real-time chat widget with citations
│   │   └── TraceFlowModal.tsx     # Visual agent timeline & metadata
│   ├── lib/api.ts                 # FastAPI client & SSE stream reader
│   ├── package.json
│   └── Dockerfile                 # Multi-stage Next.js Dockerfile
│
├── docs/                          # Architecture & Engineering Specs
│   ├── hld.md                     # High-Level Design Document
│   ├── lld.md                     # Low-Level Design Document
│   └── wireframes.md              # UI/UX & Wireframe Specifications
│
├── test.py                        # Euri LLM API verification
├── test_db.py                     # Neon PostgreSQL verification (psycopg 3)
├── test_pinecone.py               # Pinecone Vector Store verification
├── test_backend.py                # Full-stack backend & LangGraph E2E test
├── render.yaml                    # Render Blueprint deployment configuration
├── docker-compose.yml             # Single-command local full-stack runner
└── requirements.txt               # Backend dependencies
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.12+ (e.g. Conda or standard venv)
- Node.js 20.9+ & npm
- Valid `.env` configuration file in project root

### 2. Configure Environment (`.env`)
```env
# Euri LLM Gateway
EURI_API_KEY="your-euri-api-key"
EURI_BASE_URL="https://api.euron.one/api/v1/euri"
DEFAULT_MODEL="gpt-6-luna"

# Neon PostgreSQL Database
DATABASE_URL="postgresql://user:password@ep-host.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
ASYNC_DATABASE_URL="postgresql+asyncpg://user:password@ep-host.ap-southeast-1.aws.neon.tech/neondb?ssl=require"

# Pinecone Vector Database
PINECONE_API_KEY="your-pinecone-api-key"
PINECONE_INDEX_NAME="support-knowledge-base"
PINECONE_HOST="https://support-knowledge-base-xxx.svc.aped-4627-b74a.pinecone.io"
EMBEDDING_MODEL="text-embedding-3-small"
EMBEDDING_DIMENSION=1536

# Clerk SSO
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="your-clerk-publishable-key"
CLERK_SECRET_KEY="your-clerk-secret-key"

# Security
APP_SECRET="autonomous-support-platform-secret-key"
```

### 3. Run Backend (FastAPI)
```bash
# In project root
pip install -r requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Gateway: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`

### 4. Run Frontend (Next.js 16)
```bash
cd frontend
npm install
npm run dev -- -p 3000
```
- Open **`http://localhost:3000`** in your browser.

---

## 🧪 Comprehensive Verification Suite

Run all verification scripts to test every subsystem independently:

```bash
# 1. Test Euri LLM (Chat, Pydantic Structured Output, Token Streaming)
python3 test.py

# 2. Test Neon PostgreSQL (psycopg 3 Sync/Async, asyncpg, SQLAlchemy)
python3 test_db.py

# 3. Test Pinecone Vector Store (Embedding generation, upsert, semantic search)
python3 test_pinecone.py

# 4. Test Full Backend & Multi-Agent Flow (FastAPI lifespan, tickets, HITL, LangGraph)
python3 test_backend.py

# 5. Verify Next.js Production Build
cd frontend && npm run build
```

---

## ☁️ Deploying on Render

This repository includes a turnkey **`render.yaml`** blueprint for Render:

1. Push this repository to GitHub or GitLab.
2. In the [Render Dashboard](https://dashboard.render.com), navigate to **Blueprints** -> **New Blueprint Instance**.
3. Select this repository.
4. Render will automatically parse `render.yaml` and provision:
   - **`support-agent-backend`**: FastAPI Python Web Service in Singapore (`ap-southeast-1`).
   - **`support-agent-frontend`**: Next.js 16 Node Web Service with auto-linked backend URL.
5. Provide your environment secrets (`EURI_API_KEY`, `DATABASE_URL`, `PINECONE_API_KEY`, `CLERK_SECRET_KEY`) in the Render Dashboard.
6. Click **Apply** to deploy live!

---

## 👥 Contributors & Maintainers

- **Shriman Narayan** — *Platform Administrator & Lead AI Engineer* ([student.shriman@gmail.com](mailto:student.shriman@gmail.com))

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
