"""
Base rule interface for documentation and type hints.
All rule evaluators follow this pattern.
"""
from typing import Dict, Any
from models.schemas import RuleEvaluation


async def evaluate(*, policy_config: Dict[str, Any], **kwargs) -> RuleEvaluation:
    """
    Base pattern for rule evaluation.

    Every rule receives its policy config section and request context,
    and returns a RuleEvaluation with status PASS or FAIL.

    Rules must:
    - Be completely generic (no hardcoded business values)
    - Handle infrastructure errors gracefully (fail-closed)
    - Return structured reasons on failure
    """
    raise NotImplementedError
