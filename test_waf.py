import requests
import json
import time

WAF_URL = "http://localhost/api/v1/proxy/execute"

def test_waf():
    # Wait for nginx to come back up
    time.sleep(10)
    
    print("Testing WAF rules...")

    # 1. Test: crm_read(C101) Expected: ALLOW
    res1 = requests.post(WAF_URL, json={
        "agent_id": "support-agent-01",
        "session_id": "sess-test",
        "tool_name": "crm_read",
        "parameters": {"customer_id": "C101"}
    })
    print(f"Test 1 (crm_read C101): {res1.status_code}")
    print(res1.text)
    
    # 2. Test: crm_read(C999) Expected: BLOCK data_scope
    res2 = requests.post(WAF_URL, json={
        "agent_id": "support-agent-01",
        "session_id": "sess-test",
        "tool_name": "crm_read",
        "parameters": {"customer_id": "C999"}
    })
    print(f"Test 2 (crm_read C999): {res2.status_code}")
    print(res2.text)
    
    # 3. Test: crm_update(action="delete") Expected: BLOCK parameter_validation
    res3 = requests.post(WAF_URL, json={
        "agent_id": "support-agent-01",
        "session_id": "sess-test",
        "tool_name": "crm_update",
        "parameters": {"customer_id": "C101", "action": "delete"}
    })
    print(f"Test 3 (crm_update delete): {res3.status_code}")
    print(res3.text)
    
    # 4. Test: crm_delete(C101) Expected: BLOCK tool_authorization
    res4 = requests.post(WAF_URL, json={
        "agent_id": "support-agent-01",
        "session_id": "sess-test",
        "tool_name": "crm_delete",
        "parameters": {"customer_id": "C101"}
    })
    print(f"Test 4 (crm_delete C101): {res4.status_code}")
    print(res4.text)
    
    # 5. Test sequence: crm_update without authenticate_user Expected: BLOCK sequence
    # Use a fresh session id to ensure no prior auth
    res5 = requests.post(WAF_URL, json={
        "agent_id": "support-agent-01",
        "session_id": "sess-test-fresh",
        "tool_name": "crm_update",
        "parameters": {"customer_id": "C101", "action": "update"}
    })
    print(f"Test 5 (crm_update without auth): {res5.status_code}")
    print(res5.text)

if __name__ == "__main__":
    test_waf()
