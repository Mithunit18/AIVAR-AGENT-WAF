"""
Sequence Checker — Redis-backed session sequence enforcement.
Validates tool prerequisites from policy. Only records execution on PASS.
Uses agent_id + session_id for isolation. Fail-closed on Redis errors.
"""
import logging
from typing import List, Dict, Any

from redis.asyncio import Redis
from models.schemas import RuleEvaluation

logger = logging.getLogger("agent_waf")


async def check_sequence(
    redis_client: Redis,
    agent_id: str,
    session_id: str,
    tool_name: str,
    sequence_rules: List[Dict[str, str]],
) -> RuleEvaluation:
    """
    Check if the tool's prerequisites have been executed in this session.
    Only records the tool execution after all rules pass (called separately).

    Args:
        redis_client: Redis connection
        agent_id: Agent identifier
        session_id: Session identifier
        tool_name: The tool being invoked
        sequence_rules: List of {"tool": "X", "requires": "Y"} from policy
    """
    try:
        # Find if any sequence rule applies to the current tool
        for rule in sequence_rules:
            if rule.get("tool") == tool_name:
                prerequisite = rule.get("requires")
                if not prerequisite:
                    continue

                # Check if the prerequisite has been executed in this session
                state_key = f"waf:session:{agent_id}:{session_id}"
                has_prereq = await redis_client.sismember(state_key, prerequisite)

                if not has_prereq:
                    return RuleEvaluation(
                        rule="sequence",
                        status="FAIL",
                        reason=(
                            f"Tool '{tool_name}' requires prerequisite "
                            f"'{prerequisite}' to be executed first"
                        ),
                    )

        return RuleEvaluation(rule="sequence", status="PASS")

    except Exception as e:
        # Fail-closed: deny if Redis is unreachable
        logger.error(f"sequence_check_redis_error: {e}")
        return RuleEvaluation(
            rule="sequence",
            status="FAIL",
            reason="Sequence check failed: infrastructure unavailable",
        )


async def record_tool_execution(
    redis_client: Redis,
    agent_id: str,
    session_id: str,
    tool_name: str,
    session_ttl: int = 3600,
):
    """
    Record a successful tool execution in the session state.
    Called ONLY after all rules pass and tool is executed.
    """
    try:
        state_key = f"waf:session:{agent_id}:{session_id}"
        await redis_client.sadd(state_key, tool_name)
        await redis_client.expire(state_key, session_ttl)
    except Exception as e:
        logger.error(f"sequence_record_error: {e}")
