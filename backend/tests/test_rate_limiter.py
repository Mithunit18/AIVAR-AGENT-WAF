import pytest
import asyncio
from unittest.mock import AsyncMock
from rules_engine.rate_limiter import check_rate_limit

@pytest.mark.asyncio
async def test_rate_limiter_allow():
    mock_redis = AsyncMock()
    # Script returns 1 meaning allowed
    mock_redis.eval.return_value = 1
    
    result = await check_rate_limit(mock_redis, "agent-1", max_calls=10, window_seconds=60)
    
    assert result.status == "PASS"
    assert result.rule == "rate_limit"

@pytest.mark.asyncio
async def test_rate_limiter_block():
    mock_redis = AsyncMock()
    # Script returns 0 meaning blocked
    mock_redis.eval.return_value = 0
    
    result = await check_rate_limit(mock_redis, "agent-1", max_calls=10, window_seconds=60)
    
    assert result.status == "FAIL"
    assert "Rate limit exceeded" in result.reason

@pytest.mark.asyncio
async def test_rate_limiter_redis_failure():
    mock_redis = AsyncMock()
    mock_redis.eval.side_effect = Exception("Redis connection failed")
    
    # Fail-closed design: should block if Redis fails
    result = await check_rate_limit(mock_redis, "agent-1", max_calls=10, window_seconds=60)
    
    assert result.status == "FAIL"
    assert "infrastructure unavailable" in result.reason
