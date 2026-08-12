import pytest
import asyncio
import httpx
from main import app, lifespan
from datetime import datetime, timezone
import time
from tools.mock_tools import get_execution_count, reset_execution_counts

BASE_URL = "http://test"

@pytest.fixture(autouse=True)
async def setup_app_state():
    async with lifespan(app):
        yield

@pytest.fixture(autouse=True)
def reset_counts():
    reset_execution_counts()

@pytest.fixture
def base_request():
    return {
        "agent_id": "support-agent-01",
        "session_id": f"test-sess-{time.time()}",
        "tool_name": "crm_update",
        "parameters": {
            "customer_id": "C101",
            "action": "update"
        }
    }

@pytest.mark.asyncio
async def test_sequence_violation(base_request):
    """Test calling crm_update without prior authentication blocks the request."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        # Directly call crm_update
        response = await client.post("/api/v1/proxy/execute", json=base_request)
        
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["decision"] == "BLOCK"
        
        # Verify sequence rule failed
        rule_evals = {r["rule"]: r["status"] for r in data["rule_evaluations"]}
        assert rule_evals.get("sequence") == "FAIL"
        
        # Verify tool actually didn't run
        assert get_execution_count("crm_update") == 0

@pytest.mark.asyncio
async def test_default_policy_production(base_request):
    """
    Test specifically against the actual seeded support-agent-01 policy.
    Proves that the real system inherently blocks bypass attempts without
    mocking a policy for it, and allows the safe actions.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        # 1. Verify policy exists and has tool_permissions
        res = await client.get("/api/v1/policies/support-agent-01")
        assert res.status_code == 200
        policy = res.json()
        assert "tool_permissions" in policy
        assert policy["tool_permissions"].get("crm_delete", {}).get("enabled") is False
        
        # 2. Test crm_read is allowed
        read_req = dict(base_request)
        read_req["tool_name"] = "crm_read"
        res_read = await client.post("/api/v1/proxy/execute", json=read_req)
        assert res_read.status_code == 200
        assert res_read.json()["decision"] == "ALLOW"
        
        # 3. Test crm_delete is blocked
        del_req = dict(base_request)
        del_req["tool_name"] = "crm_delete"
        res_del = await client.post("/api/v1/proxy/execute", json=del_req)
        assert res_del.status_code == 403
        data = res_del.json()
        assert data["decision"] == "BLOCK"
        rule_evals = {r["rule"]: r["status"] for r in data["rule_evaluations"]}
        assert rule_evals.get("tool_authorization") == "FAIL"
        
        # 4. Verify tool execution count
        assert get_execution_count("crm_delete") == 0

@pytest.mark.asyncio
async def test_scope_violation(base_request):
    """Test calling crm_read for an unauthorized customer blocks the request."""
    base_request["tool_name"] = "crm_read"
    base_request["parameters"]["customer_id"] = "C999" # Not allowed in default policy
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        response = await client.post("/api/v1/proxy/execute", json=base_request)
        
        assert response.status_code == 403
        data = response.json()
        assert data["decision"] == "BLOCK"
        
        # Verify scope enforcer failed
        rule_evals = {r["rule"]: r["status"] for r in data["rule_evaluations"]}
        assert rule_evals.get("data_scope") == "FAIL"
        
        # Verify tool didn't run
        assert get_execution_count("crm_read") == 0

@pytest.mark.asyncio
async def test_parameter_violation(base_request):
    """Test calling crm_update with action='delete' blocks the request."""
    base_request["parameters"]["action"] = "delete" # Blocked keyword
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        response = await client.post("/api/v1/proxy/execute", json=base_request)
        
        assert response.status_code == 403
        data = response.json()
        assert data["decision"] == "BLOCK"
        
        # Verify parameter validator failed
        rule_evals = {r["rule"]: r["status"] for r in data["rule_evaluations"]}
        assert rule_evals.get("parameter_validation") == "FAIL"
        
        # Verify tool didn't run
        assert get_execution_count("crm_update") == 0

@pytest.mark.asyncio
async def test_tool_authorization(base_request):
    """Test calling crm_delete directly blocks the request due to policy tool_permissions."""
    base_request["tool_name"] = "crm_delete"
    base_request["agent_id"] = f"tool-auth-test-{time.time()}"
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        policy = {
            "agent_id": base_request["agent_id"],
            "tool_permissions": {
                "crm_delete": {"enabled": False}
            }
        }
        await client.post("/api/v1/policies/", json=policy)
        
        response = await client.post("/api/v1/proxy/execute", json=base_request)
        
        assert response.status_code == 403
        data = response.json()
        assert data["decision"] == "BLOCK"
        
        # Verify tool_authorization failed
        rule_evals = {r["rule"]: r["status"] for r in data["rule_evaluations"]}
        assert rule_evals.get("tool_authorization") == "FAIL"
        
        # Verify tool didn't run
        assert get_execution_count("crm_delete") == 0

@pytest.mark.asyncio
async def test_rate_limit(base_request):
    """Test exactly 5 requests succeed, and the 6th blocks within the window."""
    base_request["tool_name"] = "crm_read" # crm_read has no sequence prereq
    
    # We must use a unique agent_id to not collide with other tests
    base_request["agent_id"] = f"rl-test-agent-{time.time()}"
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        # We need to setup a policy for this new agent first, or use a known one.
        # Actually, let's just use the default agent and clear its rate limit in redis, 
        # or just expect that we might hit it sooner if other tests ran.
        # To be safe, we'll create a new policy via the API for testing.
        policy = {
            "agent_id": base_request["agent_id"],
            "rate_limit": {"enabled": True, "max_calls": 5, "window_seconds": 60}
        }
        await client.post("/api/v1/policies/", json=policy)
        
        # Send 5 requests
        for i in range(5):
            res = await client.post("/api/v1/proxy/execute", json=base_request)
            assert res.status_code == 200
            assert res.json()["decision"] == "ALLOW"
            
        # 6th request should fail
        res = await client.post("/api/v1/proxy/execute", json=base_request)
        assert res.status_code == 403
        data = res.json()
        assert data["decision"] == "BLOCK"
        rule_evals = {r["rule"]: r["status"] for r in data["rule_evaluations"]}
        assert rule_evals.get("rate_limit") == "FAIL"

@pytest.mark.asyncio
async def test_concurrent_rate_limit(base_request):
    """Proves the atomicity of the Lua script rate limiter."""
    base_request["tool_name"] = "crm_read"
    base_request["agent_id"] = f"rl-concurrent-{time.time()}"
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        policy = {
            "agent_id": base_request["agent_id"],
            "rate_limit": {"enabled": True, "max_calls": 5, "window_seconds": 60}
        }
        await client.post("/api/v1/policies/", json=policy)
        
        # Send 20 concurrent requests
        tasks = [
            client.post("/api/v1/proxy/execute", json=base_request)
            for _ in range(20)
        ]
        results = await asyncio.gather(*tasks)
        
        allowed_count = 0
        blocked_count = 0
        for res in results:
            if res.status_code == 200 and res.json()["decision"] == "ALLOW":
                allowed_count += 1
            elif res.status_code == 403 and res.json()["decision"] == "BLOCK":
                blocked_count += 1
                
        # We must exactly allow 5, and block the other 15!
        assert allowed_count == 5
        assert blocked_count == 15

@pytest.mark.asyncio
async def test_shadow_mode(base_request):
    """Test that in shadow mode, violating requests are allowed but marked FAIL."""
    base_request["tool_name"] = "crm_update"
    base_request["agent_id"] = f"shadow-test-{time.time()}"
    base_request["parameters"]["action"] = "delete" # Will trigger parameter violation
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        policy = {
            "agent_id": base_request["agent_id"],
            "shadow_mode": True,
            "parameter_validation": {
                "enabled": True,
                "blocked_values": ["delete"]
            }
        }
        await client.post("/api/v1/policies/", json=policy)
        
        response = await client.post("/api/v1/proxy/execute", json=base_request)
        
        # Request should succeed (200 OK) because of shadow mode
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "ALLOW"
        assert data["mode"] == "SHADOW"
        
        # But rule evaluations should show the violation
        rule_evals = {r["rule"]: r["status"] for r in data["rule_evaluations"]}
        assert rule_evals.get("parameter_validation") == "FAIL"
        
        # Verify tool ACTUALLY ran because it's shadow mode
        assert get_execution_count("crm_update") == 1
