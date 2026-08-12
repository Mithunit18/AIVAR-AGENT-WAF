import requests
import json
import time

PROXY_URL = "http://localhost:8000/api/v1/proxy/execute"
AGENT_ID = "support-agent-01"

def print_result(name, expected_status, response):
    print(f"\n--- {name} ---")
    if response.status_code == expected_status:
        print(f"PASSED (HTTP {response.status_code})")
    else:
        print(f"FAILED (Expected HTTP {expected_status}, got {response.status_code})")
    
    try:
        data = response.json()
        print("Decision:", data.get("decision", "N/A"))
        if data.get("error"):
            print("Reason:", data["error"]["message"])
        else:
            print("Result:", data.get("result"))
    except:
        print("Response:", response.text)


# 1. Valid Sequence Start: Authenticate C101
payload = {
    "agent_id": AGENT_ID,
    "session_id": "sess-test-1",
    "tool_name": "authenticate_user",
    "parameters": {"customer_id": "C101"}
}
resp = requests.post(PROXY_URL, json=payload)
print_result("Valid Auth (Expect ALLOW)", 200, resp)

# 2. Sequence Block: CRM Update for C102 without auth
payload = {
    "agent_id": AGENT_ID,
    "session_id": "sess-test-2",
    "tool_name": "crm_update",
    "parameters": {"customer_id": "C101", "action": "update"}
}
resp = requests.post(PROXY_URL, json=payload)
print_result("Sequence Violation (Expect BLOCK)", 403, resp)

# 3. Parameter Block: action="delete"
payload = {
    "agent_id": AGENT_ID,
    "session_id": "sess-test-1", # using authenticated session
    "tool_name": "crm_update",
    "parameters": {"customer_id": "C101", "action": "delete"}
}
resp = requests.post(PROXY_URL, json=payload)
print_result("Parameter Violation - delete (Expect BLOCK)", 403, resp)

# 4. Scope Block: C999
payload = {
    "agent_id": AGENT_ID,
    "session_id": "sess-test-3",
    "tool_name": "authenticate_user",
    "parameters": {"customer_id": "C999"}
}
resp = requests.post(PROXY_URL, json=payload)
print_result("Scope Violation - C999 (Expect BLOCK)", 403, resp)

# 5. Rate Limit Block: 6 rapid requests
print("\n--- Rate Limit Check ---")
for i in range(5):
    requests.post(PROXY_URL, json={
        "agent_id": AGENT_ID,
        "session_id": "sess-test-rl",
        "tool_name": "crm_read", # no prerequisite
        "parameters": {"customer_id": "C101"}
    })

resp = requests.post(PROXY_URL, json={
    "agent_id": AGENT_ID,
    "session_id": "sess-test-rl",
    "tool_name": "crm_read",
    "parameters": {"customer_id": "C101"}
})
print_result("Rate Limit Exceeded (Expect BLOCK)", 403, resp)

print("\nTests complete!")
