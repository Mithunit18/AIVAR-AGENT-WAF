import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import os
from typing import Dict, Any

WAF_BASE_URL = os.getenv("WAF_BASE_URL", "http://localhost:8000")
WAF_PROXY_URL = f"{WAF_BASE_URL}/api/v1/proxy/execute"
AGENT_ID = os.getenv("AGENT_ID", "support-agent-01")
SESSION_ID = "sess-999"

# Configure robust HTTP session
session = requests.Session()
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

def call_waf_tool(tool_name: str, parameters: Dict[str, Any]):
    payload = {
        "agent_id": AGENT_ID,
        "session_id": SESSION_ID,
        "tool_name": tool_name,
        "parameters": parameters
    }
    
    # Safe diagnostic logging (no secrets)
    print(f"\nWAF REQUEST:")
    print(f"tool={tool_name}\nagent={AGENT_ID}\nsession={SESSION_ID}\nurl={WAF_PROXY_URL}")
    
    try:
        # We explicitly set a timeout (connect timeout 5s, read timeout 15s)
        response = session.post(WAF_PROXY_URL, json=payload, timeout=(5, 15))
        
        # We return the JSON regardless of status code if it's a valid WAF response
        try:
            resp_json = response.json()
            
            # WAF RESPONSE logging
            status_code = response.status_code
            decision = resp_json.get("decision", "UNKNOWN")
            print(f"WAF RESPONSE:")
            print(f"status={status_code}\ndecision={decision}\ntool={tool_name}\n")
            
            return json.dumps(resp_json) # Return structured JSON to LangGraph
            
        except ValueError:
            # Not a JSON response, likely an HTTP error (e.g. 502 Bad Gateway from Nginx)
            print(f"WAF RESPONSE:")
            print(f"status={response.status_code}\ndecision=ERROR\ntool={tool_name}\n")
            return f"Error: HTTP {response.status_code} - {response.text}"

    except requests.exceptions.RequestException as e:
        print(f"WAF RESPONSE:")
        print(f"status=NETWORK_ERROR\ndecision=ERROR\ntool={tool_name}\n")
        return f"Error: Unable to connect to WAF at {WAF_BASE_URL} ({str(e)})"


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
