"""
Rate Limiter — Redis-backed sliding window with Lua script for atomicity.
No hardcoded limits; all values come from policy config.
"""
import logging
import time

from redis.asyncio import Redis
from models.schemas import RuleEvaluation

logger = logging.getLogger("agent_waf")

# Lua script: atomic sliding-window rate limit
# KEYS[1] = rate limit key
# ARGV[1] = current timestamp
# ARGV[2] = window start (current - window_seconds)
# ARGV[3] = max_calls
# ARGV[4] = window_seconds (for key expiry)
# Returns: 1 if allowed, 0 if blocked
RATE_LIMIT_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window_start = tonumber(ARGV[2])
local max_calls = tonumber(ARGV[3])
local window_seconds = tonumber(ARGV[4])

-- Remove expired entries
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

-- Count current entries
local count = redis.call('ZCARD', key)

if count >= max_calls then
    return 0
end

-- Add current request with unique member (timestamp:random)
redis.call('ZADD', key, now, now .. ':' .. math.random(1000000))
redis.call('EXPIRE', key, window_seconds)

return 1
"""


async def check_rate_limit(
    redis_client: Redis,
    agent_id: str,
    max_calls: int,
    window_seconds: int,
) -> RuleEvaluation:
    """
    Evaluate rate limit rule using atomic Lua script.
    Fail-closed: if Redis is unavailable, block the request.
    """
    try:
        current_time = int(time.time() * 1000)  # millisecond precision
        window_start = current_time - (window_seconds * 1000)
        key = f"waf:rate_limit:{agent_id}"

        result = await redis_client.eval(
            RATE_LIMIT_LUA,
            1,
            key,
            str(current_time),
            str(window_start),
            str(max_calls),
            str(window_seconds),
        )

        if result == 0:
            return RuleEvaluation(
                rule="rate_limit",
                status="FAIL",
                reason=f"Rate limit exceeded: {max_calls} calls per {window_seconds}s",
            )

        return RuleEvaluation(rule="rate_limit", status="PASS")

    except Exception as e:
        # Fail-closed: deny if Redis is unreachable
        logger.error(f"rate_limit_redis_error: {e}")
        return RuleEvaluation(
            rule="rate_limit",
            status="FAIL",
            reason="Rate limit check failed: infrastructure unavailable",
        )
