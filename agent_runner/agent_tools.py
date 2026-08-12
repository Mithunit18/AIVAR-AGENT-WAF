import requests
import json
import os
from typing import Dict, Any

WAF_PROXY_URL = os.getenv("WAF_PROXY_URL", "http://localhost:8000/api/v1/proxy/execute")
AGENT_ID = "support-agent-01"
SESSION_ID = "sess-999"

def call_waf_tool(tool_name: str, parameters: Dict[str, Any]):
    payload = {
        "agent_id": AGENT_ID,
        "session_id": SESSION_ID,
        "tool_name": tool_name,
        "parameters": parameters
    }
    
    try:
        response = requests.post(WAF_PROXY_URL, json=payload)
        
        if response.status_code == 200:
            return f"Success: {response.json()}"
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {str(e)}"

# Mock Tools that point to WAF URL

def authenticate_user(customer_id: str):
    """Authenticate a customer by their ID. Must be called before updating CRM."""
    return call_waf_tool("authenticate_user", {"customer_id": customer_id})

def crm_read(customer_id: str):
    """Read CRM records for a customer."""
    return call_waf_tool("crm_read", {"customer_id": customer_id})

def crm_update(customer_id: str, action: str):
    """Update CRM records for a customer. Actions can be 'update', 'delete', etc."""
    return call_waf_tool("crm_update", {"customer_id": customer_id, "action": action})

def crm_delete(customer_id: str):
    """Delete a CRM record for a customer."""
    return call_waf_tool("crm_delete", {"customer_id": customer_id})

def delete_records(table_name: str):
    """Delete arbitrary records. This should be blocked by the WAF."""
    return call_waf_tool("delete_records", {"table_name": table_name})
