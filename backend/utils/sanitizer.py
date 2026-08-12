"""
Parameter sanitizer — masks sensitive fields before audit logging and SSE.
Never stores passwords, tokens, API keys, or secrets in plain text.
"""
import copy
from typing import Any, Dict

# Fields that must be redacted (case-insensitive check)
SENSITIVE_FIELDS = frozenset({
    "password",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "secret",
    "access_token",
    "refresh_token",
    "private_key",
    "secret_key",
    "credentials",
})

REDACTED = "***REDACTED***"


def sanitize_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep-clone and recursively mask sensitive fields.
    Returns a new dict — never mutates the original.
    """
    if not params:
        return {}
    return _sanitize_value(copy.deepcopy(params))


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sanitize_field(k, v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    return value


def _sanitize_field(key: str, value: Any) -> Any:
    if key.lower() in SENSITIVE_FIELDS:
        return REDACTED
    return _sanitize_value(value)
