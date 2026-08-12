"""
Mock tool implementations.
These simulate real backend services that the agent would interact with.
"""
from typing import Dict, Any
from datetime import datetime, timezone
from collections import defaultdict

execution_counts = defaultdict(int)

def reset_execution_counts():
    """Reset all execution tracking counters."""
    execution_counts.clear()

def get_execution_count(tool_name: str) -> int:
    """Get how many times a tool was actually executed."""
    return execution_counts[tool_name]


async def authenticate_user(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate authenticating a user/customer."""
    execution_counts["authenticate_user"] += 1
    customer_id = parameters.get("customer_id", "unknown")
    return {
        "authenticated": True,
        "customer_id": customer_id,
        "session_token": "mock-session-token-xyz",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def crm_read(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate reading CRM data for a customer."""
    execution_counts["crm_read"] += 1
    customer_id = parameters.get("customer_id", "unknown")
    return {
        "customer_id": customer_id,
        "name": f"Customer {customer_id}",
        "email": f"{customer_id.lower()}@example.com",
        "status": "active",
    }


async def crm_update(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate updating CRM data."""
    execution_counts["crm_update"] += 1
    customer_id = parameters.get("customer_id", "unknown")
    action = parameters.get("action", "update")
    return {
        "customer_id": customer_id,
        "action": action,
        "status": "completed",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


async def crm_delete(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate deleting CRM records."""
    execution_counts["crm_delete"] += 1
    customer_id = parameters.get("customer_id", "unknown")
    return {
        "customer_id": customer_id,
        "action": "delete",
        "status": "completed",
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }


async def send_email(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate sending an email."""
    execution_counts["send_email"] += 1
    return {
        "to": parameters.get("to", "unknown"),
        "subject": parameters.get("subject", "No subject"),
        "status": "sent",
        "message_id": "mock-msg-001",
    }


async def delete_records(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate deleting database records."""
    execution_counts["delete_records"] += 1
    table_name = parameters.get("table_name", "unknown")
    return {
        "table": table_name,
        "action": "delete",
        "status": "completed",
    }
