# Wireframes & UI/UX Specification Document
## Autonomous Customer Support & Resolution Platform

---

### 1. UI Architecture & View Hierarchy

The Next.js frontend is structured into two dedicated portals sharing a common design system (Tailwind CSS, Lucide icons, Dark/Light mode):

```
Frontend Views
├── 1. Customer Interaction Portal (/customer)
│   ├── Floating / Full-screen Support Chat Widget
│   ├── Real-Time Streaming Message Feed (SSE)
│   ├── Cited Reference Cards (Grounding)
│   └── Ticket Status & Resolution Summary
│
└── 2. Support Agent Operations Dashboard (/dashboard)
    ├── Overview & Metrics Banner (SLA, Triage Count, Auto-Resolution Rate)
    ├── Real-Time Ticket Triage Feed (Severity Badges: P0-P3, Status Filters)
    ├── HITL Action Center (/dashboard/hitl)
    │   ├── Pending High-Risk Action Cards
    │   ├── Action Diff & Risk Justification Viewer
    │   └── One-Click Approve / Modify / Reject Controls
    └── Ticket Deep Dive & Agent Trace Flow (/dashboard/tickets/[id])
        ├── Interactive LangGraph Execution Timeline
        ├── Node Inputs, Thoughts & Tool Call Inspections
        └── Manual Override & Operator Reply Panel
```

---

### 2. Screen 1: Customer Interaction Portal (`/customer`)

```text
+----------------------------------------------------------------------------------------------------+
|  [Logo] CloudScale Enterprise Support                         [Status: All Systems Operational]    |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  +----------------------------------------------------------------------------------------------+  |
|  | Ticket #TK-8910: Duplicate Charge on Invoice #INV-9821            [Severity: P1] [In Progress] |  |
|  +----------------------------------------------------------------------------------------------+  |
|  |                                                                                              |  |
|  |  [User @ 10:14 AM]                                                                           |  |
|  |  I was charged $89 twice for my renewal this morning on invoice #INV-9821. Please refund!    |  |
|  |                                                                                              |  |
|  |  [Autonomous Support Agent @ 10:14 AM]                                                       |  |
|  |  Hello Alex! I am investigating this immediately for you.                                    |  |
|  |                                                                                              |  |
|  |  +----------------------------------------------------------------------------------------+  |
|  |  | 🔍 Investigating: Checked Stripe Transactions -> Duplicate charge verified on INV-9821.  |  |
|  |  +----------------------------------------------------------------------------------------+  |
|  |                                                                                              |  |
|  |  I have generated a resolution to refund the $89.00 duplicate charge.                        |  |
|  |  Because this involves a financial transaction over $50, our team is providing a quick       |  |
|  |  sign-off. You will receive an instant confirmation as soon as it completes.                |  |
|  |                                                                                              |  |
|  |  +----------------------------------------------------------------------------------------+  |
|  |  | 📚 Cited Policy: Billing KB-401 - Duplicate Subscription Refunds (Full refund in 1-3d)    |  |
|  |  +----------------------------------------------------------------------------------------+  |
|  |                                                                                              |  |
|  +----------------------------------------------------------------------------------------------+  |
|  | [Type your message or inquiry here...                                              ] [ Send ]|  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

### 3. Screen 2: Support Agent Operations Dashboard (`/dashboard`)

```text
+----------------------------------------------------------------------------------------------------+
|  [Logo] Support Ops Center    [Search tickets...]     (Active Queue: 12)  [🔔 3 HITL]  [Agent Sarah]|
+----------------------------------------------------------------------------------------------------+
|  [ Metrics Banner ]                                                                                |
|  +-------------------+  +-------------------+  +-------------------+  +-------------------------+  |
|  | Open Tickets: 14  |  | HITL Gated: 3     |  | Auto-Resolve: 82% |  | Avg Resolution: 2.1m   |  |
|  +-------------------+  +-------------------+  +-------------------+  +-------------------------+  |
|                                                                                                    |
|  [Filters: All | P0 Outages | P1 Financial | P2 Feature | P3 Minor]   [Status: All | Pending HITL]  |
|                                                                                                    |
|  +----------------------------------------------------------------------------------------------+  |
|  | ID      | Customer       | Title / Issue Summary               | Severity | Status  | Action |  |
|  |---------|----------------|-------------------------------------|----------|---------|--------|  |
|  | #TK-8910| Acme Corp (Ent)| Duplicate Charge on #INV-9821       | [P1]     | [HITL]  |[Review]|  |
|  | #TK-8909| VercelDev (Pro)| API Rate Limit 429 after upgrade    | [P2]     | [Resolv]|[Inspect|  |
|  | #TK-8908| DataFlow (Ent) | Cluster Node 3 Connection Drop      | [P0]     | [Invest]|[Trace] |  |
|  | #TK-8907| SoloDev (Free) | How to export CSV reports?          | [P3]     | [Closed]|[View]  |  |
|  +----------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
```

---

### 4. Screen 3: Human-in-the-Loop (HITL) Action Center (`/dashboard/hitl`)

```text
+----------------------------------------------------------------------------------------------------+
|  [< Back to Dashboard]  HITL Action Review Center                         [3 Actions Pending Review]|
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  +----------------------------------------------------------------------------------------------+  |
|  | ⚠️ HIGH-RISK ACTION FLAGGED: Financial Mutation                               [Ticket #TK-8910]  |  |
|  | Customer: Acme Corp (Enterprise Tier) | Requested By: Autonomous Resolution Agent             |  |
|  +----------------------------------------------------------------------------------------------+  |
|  |                                                                                              |  |
|  |  RISK TRIGGER:                                                                               |  |
|  |  "Action 'issue_refund' exceeds automated safety threshold ($89.00 > $50.00 ceiling)."      |  |
|  |                                                                                              |  |
|  |  INVESTIGATION SNAPSHOT:                                                                     |  |
|  |  - Invoice: #INV-9821 ($89.00 billed 2026-10-20 08:30:12 UTC)                               |  |
|  |  - Duplicate: #INV-9820 ($89.00 billed 2026-10-20 08:30:10 UTC)                              |  |
|  |  - Telemetry: Double webhook trigger detected from Stripe subscription renewal.              |  |
|  |                                                                                              |  |
|  |  PROPOSED ACTION PAYLOAD:                                                                    |  |
|  |  ```json                                                                                     |  |
|  |  {                                                                                           |  |
|  |    "action": "stripe_issue_refund",                                                          |  |
|  |    "invoice_id": "INV-9821",                                                                 |  |
|  |    "amount": 89.00,                                                                          |  |
|  |    "reason": "Duplicate charge on automatic renewal"                                         |  |
|  |  }                                                                                           |  |
|  |  ```                                                                                         |  |
|  |                                                                                              |  |
|  |  OPERATOR CONTROLS:                                                                          |  |
|  |  [Notes: Verified duplicate transaction webhook. Ready to execute.                        ]  |  |
|  |                                                                                              |  |
|  |  [ ✅ APPROVE ACTION ]      [ ✏️ MODIFY PAYLOAD ]      [ ❌ REJECT & RETURN TO AGENT ]        |  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

### 5. Screen 4: Visual Agent Trace & Execution Flow (`/dashboard/tickets/[id]`)

```text
+----------------------------------------------------------------------------------------------------+
|  Ticket #TK-8910 Execution Flow Trace                            [Agent: LangGraph Multi-Agent]    |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [Step 1: Supervisor Router] -----------------------------------------------------> [0.82s] ✅     |
|  • Input: "I was charged $89 twice on invoice #INV-9821..."                                        |
|  • Output: Intent: Billing Dispute | Severity: P1 Financial | Route -> Troubleshooting             |
|                                                                                                    |
|  [Step 2: Troubleshooting Agent] -------------------------------------------------> [1.14s] ✅     |
|  • MCP Tool: `get_invoices_and_charges(customer_id='cust_901')`                                    |
|  • Findings: Confirmed 2 charges of $89.00 within 2 seconds. Identical idempotency keys missed.    |
|                                                                                                    |
|  [Step 3: Knowledge / RAG Agent] -------------------------------------------------> [0.65s] ✅     |
|  • Pinecone Vector Query + gpt-6-luna Reranker: Retrieved KB-401 (Score: 0.94)                    |
|  • Policy Match: Duplicate charges refundable without penalty.                                     |
|                                                                                                    |
|  [Step 4: Resolution Agent] ------------------------------------------------------> [0.91s] ⏸️     |
|  • Synthesized Plan: Refund Invoice #INV-9821                                                      |
|  • Safety Assessment: Amount ($89.00) > $50.00 Limit -> TRIGGER HITL INTERRUPT                     |
|                                                                                                    |
|  [Step 5: HITL Gate (Current State)] ---------------------------------------------> [PAUSED] ⏸️    |
|  • Checkpoint saved in Neon PostgreSQL. Waiting for operator review...                            |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```
