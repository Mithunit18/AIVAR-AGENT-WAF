"""
FastAPI middleware for request ID propagation and structured logging.
"""
import uuid
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("agent_waf")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Reads X-Request-ID from incoming request headers, or generates a UUID.
    Attaches it to request.state.request_id and adds it to the response header.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()

        response = await call_next(request)

        latency_ms = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id

        # Structured log for every request (skip health checks at DEBUG)
        path = request.url.path
        if path in ("/health", "/ready"):
            logger.debug(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "status": response.status_code,
                    "latency_ms": round(latency_ms, 2),
                },
            )
        else:
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "status": response.status_code,
                    "latency_ms": round(latency_ms, 2),
                },
            )

        return response
