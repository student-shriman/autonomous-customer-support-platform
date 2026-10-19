"""
Standard Model Context Protocol (MCP) Operational Tools.
Exposes:
  - get_customer_profile
  - get_invoices_and_charges
  - inspect_diagnostic_logs
  - issue_refund (HIGH RISK)
  - update_subscription_tier (HIGH RISK)
"""

from typing import Dict, Any, List
import datetime

# Mock enterprise CRM & Billing Database
_MOCK_CUSTOMERS = {
    "cust_default": {
        "id": "cust_default",
        "name": "Sarah Connor",
        "company": "Cyberdyne Systems",
        "email": "sarah@cyberdyne.com",
        "tier": "enterprise",
        "status": "active",
        "mrr": 499.00,
        "subscription_id": "sub_ent_8921",
        "created_at": "2024-01-15T08:00:00Z"
    },
    "cust_acme": {
        "id": "cust_acme",
        "name": "Alex Miller",
        "company": "Acme Corp",
        "email": "alex@acme.com",
        "tier": "enterprise",
        "status": "active",
        "mrr": 299.00,
        "subscription_id": "sub_ent_9821",
        "created_at": "2024-03-10T11:20:00Z"
    }
}

_MOCK_INVOICES = {
    "cust_default": [
        {"id": "INV-9821", "amount": 89.00, "status": "paid", "date": "2026-10-20T08:30:12Z", "description": "Enterprise Add-on Renewal"},
        {"id": "INV-9820", "amount": 89.00, "status": "paid", "date": "2026-10-20T08:30:10Z", "description": "Enterprise Add-on Renewal (Duplicate Webhook)"},
        {"id": "INV-8900", "amount": 499.00, "status": "paid", "date": "2026-10-01T00:00:00Z", "description": "Monthly Enterprise Base Tier"}
    ],
    "cust_acme": [
        {"id": "INV-9821", "amount": 89.00, "status": "paid", "date": "2026-10-20T08:30:12Z", "description": "Enterprise Add-on Renewal"},
        {"id": "INV-9820", "amount": 89.00, "status": "paid", "date": "2026-10-20T08:30:10Z", "description": "Enterprise Add-on Renewal (Duplicate Webhook)"}
    ]
}

_MOCK_TELEMETRY = [
    {"timestamp": "2026-10-20T08:30:10Z", "service": "billing-webhook", "level": "WARN", "message": "Duplicate idempotency key received for checkout.session.completed"},
    {"timestamp": "2026-10-20T08:30:12Z", "service": "billing-engine", "level": "INFO", "message": "Charged invoice #INV-9821 successfully via Stripe payment intent pi_3P889"},
    {"timestamp": "2026-10-20T08:30:14Z", "service": "api-gateway", "level": "INFO", "message": "HTTP 200 OK customer webhook delivery completed"}
]

def get_customer_profile(customer_id: str) -> Dict[str, Any]:
    """Retrieve customer subscription, plan tier, and account metadata."""
    profile = _MOCK_CUSTOMERS.get(customer_id) or _MOCK_CUSTOMERS.get("cust_default")
    return {"status": "success", "profile": profile}

def get_invoices_and_charges(customer_id: str, limit: int = 5) -> Dict[str, Any]:
    """Retrieve recent billing transactions, invoices, and charges for a customer."""
    invoices = _MOCK_INVOICES.get(customer_id) or _MOCK_INVOICES.get("cust_default")
    return {"status": "success", "customer_id": customer_id, "invoices": invoices[:limit]}

def inspect_diagnostic_logs(service: str = "billing", lookback_mins: int = 60) -> Dict[str, Any]:
    """Inspect system telemetry, error spikes, and recent service logs."""
    return {
        "status": "success",
        "service": service,
        "lookback_mins": lookback_mins,
        "logs": _MOCK_TELEMETRY
    }

def issue_refund(invoice_id: str, amount: float, reason: str) -> Dict[str, Any]:
    """
    Execute a financial refund transaction.
    HIGH RISK: Mutates payment gateway state.
    """
    ref_id = f"rf_sec_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    return {
        "status": "completed",
        "action": "issue_refund",
        "refund_id": ref_id,
        "invoice_id": invoice_id,
        "amount_refunded": amount,
        "currency": "USD",
        "reason": reason,
        "processed_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

def update_subscription_tier(customer_id: str, new_tier: str) -> Dict[str, Any]:
    """
    Update customer plan tier and API quotas.
    HIGH RISK: Modifies recurring billing contract.
    """
    return {
        "status": "completed",
        "action": "update_subscription_tier",
        "customer_id": customer_id,
        "previous_tier": "starter",
        "new_tier": new_tier,
        "effective_date": "immediate"
    }
