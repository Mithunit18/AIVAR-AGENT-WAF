"""
Rule Evaluator — orchestrates all enabled rules from a policy.
Produces final ALLOW/BLOCK disposition with shadow mode support.
"""
import logging
from typing import Dict, Any, List, Tuple

from redis.asyncio import Redis
from models.schemas import RuleEvaluation
from rules_engine.rate_limiter import check_rate_limit
from rules_engine.parameter_validator import validate_parameters
from rules_engine.scope_enforcer import enforce_scope
from rules_engine.sequence_checker import check_sequence
from rules_engine.tool_authorization import evaluate as check_tool_authorization

logger = logging.getLogger("agent_waf")


async def evaluate_all_rules(
    policy: Dict[str, Any],
    agent_id: str,
    session_id: str,
    tool_name: str,
    parameters: Dict[str, Any],
    redis_client: Redis,
) -> Tuple[List[RuleEvaluation], str, str]:
    """
    Evaluate all enabled rules from the policy.

    Returns:
        (rule_evaluations, final_disposition, mode)
        - rule_evaluations: list of RuleEvaluation results
        - final_disposition: "ALLOW" or "BLOCK"
        - mode: "ENFORCE" or "SHADOW"
    """
    evaluations: List[RuleEvaluation] = []
    shadow_mode = policy.get("shadow_mode", False)

    # 1. Tool Authorization
    result = await check_tool_authorization(policy, tool_name)
    evaluations.append(result)

    # 2. Rate Limiting
    rate_limit_config = policy.get("rate_limit", {})
    if rate_limit_config.get("enabled", False):
        result = await check_rate_limit(
            redis_client,
            agent_id,
            rate_limit_config.get("max_calls", 5),
            rate_limit_config.get("window_seconds", 60),
        )
        evaluations.append(result)

    # 3. Parameter Validation
    param_config = policy.get("parameter_validation", {})
    if param_config.get("enabled", False):
        result = await validate_parameters(
            parameters,
            param_config.get("blocked_values", []),
            param_config.get("max_parameter_size", 10000),
        )
        evaluations.append(result)

    # 4. Data Scope Enforcement
    scope_config = policy.get("data_scope", {})
    if scope_config.get("enabled", False):
        result = await enforce_scope(
            parameters,
            scope_config.get("allowed_scopes", {}),
        )
        evaluations.append(result)

    # 5. Sequence Rules
    seq_config = policy.get("sequence_rules", {})
    if seq_config.get("enabled", False):
        # Convert sequence rules to list of dicts
        rules_list = seq_config.get("rules", [])
        if isinstance(rules_list, list):
            # Normalize: could be list of dicts or list of SequenceRuleItem
            normalized = []
            for r in rules_list:
                if isinstance(r, dict):
                    normalized.append(r)
                else:
                    # Pydantic model
                    normalized.append({"tool": r.tool, "requires": r.requires})
            result = await check_sequence(
                redis_client,
                agent_id,
                session_id,
                tool_name,
                normalized,
            )
            evaluations.append(result)

    # Determine final disposition
    has_failure = any(e.status == "FAIL" for e in evaluations)

    if has_failure:
        if shadow_mode:
            # Shadow mode: log violation but allow execution
            mode = "SHADOW"
            final_disposition = "ALLOW"
            logger.info(
                f"shadow_mode_violation agent_id={agent_id} tool={tool_name} "
                f"would_block=True"
            )
        else:
            mode = "ENFORCE"
            final_disposition = "BLOCK"
            failed_rules = [e.rule for e in evaluations if e.status == "FAIL"]
            logger.info(
                f"tool_blocked agent_id={agent_id} tool={tool_name} "
                f"rules={failed_rules}"
            )
    else:
        mode = "ENFORCE"
        final_disposition = "ALLOW"
        logger.info(f"tool_allowed agent_id={agent_id} tool={tool_name}")

    return evaluations, final_disposition, mode
