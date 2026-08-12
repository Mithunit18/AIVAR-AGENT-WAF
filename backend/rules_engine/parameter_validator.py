"""
Parameter Validator — generic, policy-driven parameter inspection.
Recursively inspects nested dicts/lists for blocked values.
Supports size limits. No hardcoded blocked values.
"""
import json
import logging
from typing import List, Dict, Any

from models.schemas import RuleEvaluation

logger = logging.getLogger("agent_waf")


async def validate_parameters(
    parameters: Dict[str, Any],
    blocked_values: List[str],
    max_parameter_size: int = 10000,
) -> RuleEvaluation:
    """
    Validate parameters against blocked values list and size limit.
    All blocked values come from policy — nothing is hardcoded.
    """
    if not parameters:
        return RuleEvaluation(rule="parameter_validation", status="PASS")

    # Size check
    params_json = json.dumps(parameters)
    if len(params_json) > max_parameter_size:
        return RuleEvaluation(
            rule="parameter_validation",
            status="FAIL",
            reason=f"Parameter size {len(params_json)} exceeds maximum {max_parameter_size}",
        )

    # Recursive blocked value check
    violation = _check_blocked_recursive(parameters, blocked_values)
    if violation:
        return RuleEvaluation(
            rule="parameter_validation",
            status="FAIL",
            reason=violation,
        )

    return RuleEvaluation(rule="parameter_validation", status="PASS")


def _check_blocked_recursive(value: Any, blocked_values: List[str], path: str = "") -> str | None:
    """
    Recursively walk the parameter tree, checking every string value
    against the blocked values list (case-insensitive).
    Returns the violation reason string, or None if clean.
    """
    if isinstance(value, dict):
        for k, v in value.items():
            current_path = f"{path}.{k}" if path else k
            result = _check_blocked_recursive(v, blocked_values, current_path)
            if result:
                return result
    elif isinstance(value, list):
        for i, item in enumerate(value):
            current_path = f"{path}[{i}]"
            result = _check_blocked_recursive(item, blocked_values, current_path)
            if result:
                return result
    elif isinstance(value, str):
        value_lower = value.lower()
        for blocked in blocked_values:
            if blocked.lower() in value_lower:
                return f"Blocked parameter found: '{blocked}' in field '{path}'"
    return None
