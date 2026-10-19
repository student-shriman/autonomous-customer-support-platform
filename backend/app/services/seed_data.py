"""
Seed Data Generator for Neon PostgreSQL.
Populates standard RBAC users, customer accounts, and demo tickets.
"""

import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.models.customer import CustomerProfile
from backend.app.models.ticket import Ticket, TicketMessage
from backend.app.models.hitl import HITLAction
from backend.app.models.audit import AuditLog
from backend.app.core.security import get_password_hash

async def seed_initial_data(db: AsyncSession):
    """Ensure database has initial demo records."""
    # Check if ticket data already exists
    res = await db.execute(select(Ticket).limit(1))
    if res.scalars().first():
        return

    print("[Seed] Populating initial demo accounts and tickets in Neon PostgreSQL...")

    # 1. Create RBAC Users
    admin_user = User(
        id=str(uuid.uuid4()),
        email="admin@cloudscale.io",
        hashed_password=get_password_hash("admin123"),
        full_name="System Administrator",
        role="admin"
    )

    agent_user = User(
        id=str(uuid.uuid4()),
        email="agent.sarah@cloudscale.io",
        hashed_password=get_password_hash("agent123"),
        full_name="Sarah Jenkins (Senior Support Specialist)",
        role="support_agent"
    )

    cust_user = User(
        id=str(uuid.uuid4()),
        email="alex@acme.com",
        hashed_password=get_password_hash("customer123"),
        full_name="Alex Miller",
        role="customer"
    )

    db.add_all([admin_user, agent_user, cust_user])
    await db.flush()

    # 2. Customer Profile
    acme_profile = CustomerProfile(
        id="cust_acme",
        user_id=cust_user.id,
        company_name="Acme Corp",
        tier="enterprise",
        stripe_customer_id="cus_acme_9821",
        active_subscription_id="sub_ent_9821",
        monthly_spend=299.00
    )
    db.add(acme_profile)
    await db.flush()

    # 3. Seed Demo Tickets
    # Ticket 1: High-Risk HITL Billing Dispute (P1)
    ticket_hitl = Ticket(
        id="TK-8910",
        customer_id=acme_profile.id,
        title="Duplicate Charge on Invoice #INV-9821 ($89.00)",
        status="pending_hitl",
        severity="P1",
        intent="Billing dispute - duplicate charge reversal",
        summary="Customer was charged twice for enterprise add-on renewal. Proposed refund of $89.00 flagged for human sign-off.",
        assigned_agent_id=agent_user.id,
        created_at=datetime.utcnow() - timedelta(minutes=45)
    )

    db.add(ticket_hitl)
    await db.flush()

    # Messages for Ticket 1
    msg1 = TicketMessage(
        id=str(uuid.uuid4()),
        ticket_id=ticket_hitl.id,
        sender_type="customer",
        sender_name="Alex Miller",
        content="I was charged $89 twice for my enterprise tier subscription renewal this morning on invoice #INV-9821. Please reverse the duplicate charge immediately!",
        created_at=datetime.utcnow() - timedelta(minutes=45)
    )

    msg2 = TicketMessage(
        id=str(uuid.uuid4()),
        ticket_id=ticket_hitl.id,
        sender_type="agent",
        sender_name="Autonomous Support Agent",
        content="Hello Alex! I verified invoice #INV-9821 and found a matching duplicate transaction from an automatic webhook retry. I have drafted an immediate refund of $89.00. Because this transaction exceeds $50.00, our support specialist team is giving it a quick review to ensure safety compliance.",
        citations=[{"title": "Billing KB-401: Duplicate Charge & Refund Policy", "source": "kb-billing-refund-001"}],
        agent_trace=[
            {"agent_name": "Supervisor Agent", "summary": "Classified P1 Financial Billing -> Route to Troubleshooting"},
            {"agent_name": "Troubleshooting Agent", "summary": "Found duplicate charges on #INV-9821 and #INV-9820"},
            {"agent_name": "Knowledge / RAG Agent", "summary": "Retrieved KB-401 Refund Policy via Pinecone & gpt-6-luna"},
            {"agent_name": "Resolution Agent", "summary": "Synthesized refund action. Safety check: $89 > $50 limit -> Triggered HITL"},
            {"agent_name": "Escalation Agent", "summary": "Incident package registered into HITL Action Review Queue"}
        ],
        created_at=datetime.utcnow() - timedelta(minutes=44)
    )

    # HITL Action for Ticket 1
    hitl_act = HITLAction(
        id="act_hitl_9821",
        ticket_id=ticket_hitl.id,
        action_type="issue_refund",
        proposed_payload={"invoice_id": "INV-9821", "amount": 89.00, "reason": "Duplicate subscription renewal charge"},
        risk_level="HIGH",
        risk_reason="Financial mutation > $50.00 safety threshold requires human support sign-off",
        status="pending",
        created_at=datetime.utcnow() - timedelta(minutes=44)
    )

    # Ticket 2: Resolved Technical Inquiry (P2)
    ticket_resolved = Ticket(
        id="TK-8909",
        customer_id=acme_profile.id,
        title="API Rate Limit 429 after adding background workers",
        status="resolved",
        severity="P2",
        intent="Technical inquiry regarding API quotas",
        summary="Customer exceeded 60 req/min standard quota. Guided them to enterprise rate limit headers and backoff retry.",
        assigned_agent_id=agent_user.id,
        created_at=datetime.utcnow() - timedelta(hours=3)
    )

    # Ticket 3: P0 Outage Simulation
    ticket_p0 = Ticket(
        id="TK-8908",
        customer_id=acme_profile.id,
        title="Cluster Node 3 Connection Drop in AP-South Region",
        status="investigating",
        severity="P0",
        intent="Service outage / connectivity failure",
        summary="Automated telemetry detected packet drop in database read replica.",
        assigned_agent_id=agent_user.id,
        created_at=datetime.utcnow() - timedelta(minutes=15)
    )

    db.add_all([msg1, msg2, hitl_act, ticket_resolved, ticket_p0])
    await db.commit()
    print("[Seed] Initial database seed completed successfully!")
