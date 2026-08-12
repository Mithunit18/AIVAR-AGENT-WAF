import pytest
from unittest.mock import AsyncMock
from rules_engine.sequence_checker import check_sequence, record_tool_execution

@pytest.mark.asyncio
async def test_sequence_allow_no_prereq():
    mock_redis = AsyncMock()
    rules = [{"tool": "crm_update", "requires": "authenticate_user"}]
    
    # tool "crm_read" is not in rules, so it should pass implicitly
    result = await check_sequence(mock_redis, "agent-1", "sess-1", "crm_read", rules)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_sequence_allow_with_prereq():
    mock_redis = AsyncMock()
    # Mock that authenticate_user was executed (exists in redis set)
    mock_redis.sismember.return_value = 1
    
    rules = [{"tool": "crm_update", "requires": "authenticate_user"}]
    
    result = await check_sequence(mock_redis, "agent-1", "sess-1", "crm_update", rules)
    assert result.status == "PASS"
    mock_redis.sismember.assert_called_once_with("waf:session:agent-1:sess-1", "authenticate_user")

@pytest.mark.asyncio
async def test_sequence_block_missing_prereq():
    mock_redis = AsyncMock()
    # Mock that authenticate_user was NOT executed
    mock_redis.sismember.return_value = 0
    
    rules = [{"tool": "crm_update", "requires": "authenticate_user"}]
    
    result = await check_sequence(mock_redis, "agent-1", "sess-1", "crm_update", rules)
    assert result.status == "FAIL"
    assert "requires prerequisite 'authenticate_user'" in result.reason

@pytest.mark.asyncio
async def test_sequence_redis_failure():
    mock_redis = AsyncMock()
    mock_redis.sismember.side_effect = Exception("Redis down")
    
    rules = [{"tool": "crm_update", "requires": "authenticate_user"}]
    
    # Fail-closed
    result = await check_sequence(mock_redis, "agent-1", "sess-1", "crm_update", rules)
    assert result.status == "FAIL"
    assert "infrastructure unavailable" in result.reason
