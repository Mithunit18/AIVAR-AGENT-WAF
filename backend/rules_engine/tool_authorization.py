from typing import Dict, Any
from models.schemas import RuleEvaluation

async def evaluate(
    policy: Dict[str, Any],
    tool_name: str,
) -> RuleEvaluation:
    """
    Evaluates whether the requested tool is explicitly disabled in the policy.
    Default is ALLOW if not mentioned.
    """
    tool_permissions = policy.get("tool_permissions", {})
    
    if tool_name in tool_permissions:
        tool_policy = tool_permissions[tool_name]
        if not tool_policy.get("enabled", True):
            return RuleEvaluation(
                rule="tool_authorization",
                status="FAIL",
                reason=f"Tool '{tool_name}' is disabled by policy",
            )
            
    return RuleEvaluation(
        rule="tool_authorization",
        status="PASS",
    )
