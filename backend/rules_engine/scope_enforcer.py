"""
Scope Enforcer — generic, policy-driven data scope enforcement.
Supports multiple scope keys and nested parameter lookup.
No hardcoded customer IDs or scope values.
"""
import logging
from typing import Dict, List, Any, Optional

from models.schemas import RuleEvaluation

logger = logging.getLogger("agent_waf")


async def enforce_scope(
    parameters: Dict[str, Any],
    allowed_scopes: Dict[str, List[str]],
) -> RuleEvaluation:
    """
    Check that scoped parameters are within the allowed values.
    Supports nested parameter lookup (e.g., 'customer.id').
    All allowed values come from policy.
    """
    if not parameters or not allowed_scopes:
        return RuleEvaluation(rule="data_scope", status="PASS")

    for scope_key, allowed_values in allowed_scopes.items():
        param_value = _get_nested(parameters, scope_key)
        if param_value is not None:
            if str(param_value) not in [str(v) for v in allowed_values]:
                return RuleEvaluation(
                    rule="data_scope",
                    status="FAIL",
                    reason=(
                        f"Parameter '{scope_key}' value '{param_value}' "
                        f"is outside the allowed scope {allowed_values}"
                    ),
                )

    return RuleEvaluation(rule="data_scope", status="PASS")


def _get_nested(data: Dict[str, Any], key: str) -> Optional[Any]:
    """
    Get a value from a nested dict using dot notation.
    e.g., _get_nested({"customer": {"id": "C101"}}, "customer.id") -> "C101"
    Falls back to direct key lookup for flat dicts.
    """
    # Try direct key first
    if key in data:
        return data[key]

    # Try dot-notation traversal
    parts = key.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current
