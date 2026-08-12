"""
Global exception handlers and custom exceptions for the Agent WAF.
Returns structured JSON errors, never exposes stack traces to clients.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger("agent_waf")


class PolicyNotFoundError(Exception):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        super().__init__(f"No active policy found for agent: {agent_id}")


class WAFBlockedError(Exception):
    def __init__(self, reason: str, rule_evaluations: list = None):
        self.reason = reason
        self.rule_evaluations = rule_evaluations or []
        super().__init__(reason)


class ToolNotFoundError(Exception):
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        super().__init__(f"Tool not registered: {tool_name}")


class InfrastructureError(Exception):
    """Raised when MongoDB/Redis is unreachable."""
    pass


def register_exception_handlers(app: FastAPI):
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(PolicyNotFoundError)
    async def policy_not_found_handler(request: Request, exc: PolicyNotFoundError):
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": {
                    "code": "POLICY_NOT_FOUND",
                    "message": str(exc),
                },
                "request_id": request_id,
            },
        )

    @app.exception_handler(WAFBlockedError)
    async def waf_blocked_handler(request: Request, exc: WAFBlockedError):
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": {
                    "code": "WAF_POLICY_VIOLATION",
                    "message": "Tool invocation blocked by WAF policy",
                },
                "request_id": request_id,
                "rule_evaluations": [
                    e.model_dump() if hasattr(e, "model_dump") else e
                    for e in exc.rule_evaluations
                ],
            },
        )

    @app.exception_handler(ToolNotFoundError)
    async def tool_not_found_handler(request: Request, exc: ToolNotFoundError):
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": {
                    "code": "TOOL_NOT_FOUND",
                    "message": str(exc),
                },
                "request_id": request_id,
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                },
                "request_id": request_id,
            },
        )

    @app.exception_handler(InfrastructureError)
    async def infra_error_handler(request: Request, exc: InfrastructureError):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(f"Infrastructure error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "A required service is temporarily unavailable",
                },
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                },
                "request_id": request_id,
            },
        )
