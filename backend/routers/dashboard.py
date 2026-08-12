"""
Dashboard API — SSE stream, event queries, and summary stats.
"""
import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from sse_starlette.sse import EventSourceResponse

router = APIRouter()
logger = logging.getLogger("agent_waf")


# ─── SSE Stream ───────────────────────────────────────────────────────────────

async def _event_generator(req: Request, sub_id: int, queue: asyncio.Queue):
    """Generate SSE events from the subscriber's queue."""
    try:
        while True:
            if await req.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield json.dumps(event, default=str)
            except asyncio.TimeoutError:
                # Keep-alive heartbeat
                yield json.dumps({"type": "ping"})
    finally:
        # Cleanup subscriber on disconnect
        broker = req.app.state.event_broker
        broker.unsubscribe(sub_id)


@router.get("/stream")
async def stream(request: Request):
    """SSE endpoint for real-time dashboard events. Supports multiple clients."""
    broker = request.app.state.event_broker
    sub_id, queue = broker.subscribe()
    return EventSourceResponse(_event_generator(request, sub_id, queue))


# ─── Events API ───────────────────────────────────────────────────────────────

@router.get("/events")
async def get_events(
    request: Request,
    agent_id: Optional[str] = None,
    tool_name: Optional[str] = None,
    decision: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    """Query audit events with filters and pagination."""
    audit_repo = request.app.state.audit_repo
    events, total = await audit_repo.get_events(
        agent_id=agent_id,
        tool_name=tool_name,
        decision=decision,
        start_time=start_time,
        end_time=end_time,
        limit=min(limit, 200),  # Cap at 200
        offset=offset,
    )
    return {
        "events": events,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/events/{event_id}")
async def get_event_detail(event_id: str, request: Request):
    """Get a single audit event by event_id."""
    audit_repo = request.app.state.audit_repo
    event = await audit_repo.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail={
            "code": "EVENT_NOT_FOUND",
            "message": f"No event found with id: {event_id}",
        })
    return event


@router.get("/summary")
async def get_summary(request: Request):
    """Get aggregated dashboard stats."""
    audit_repo = request.app.state.audit_repo
    return await audit_repo.get_summary()


# ─── History (backward compat) ────────────────────────────────────────────────

@router.get("/history")
async def get_history(request: Request, limit: int = 50):
    """Legacy history endpoint — redirects to events API."""
    audit_repo = request.app.state.audit_repo
    events, _ = await audit_repo.get_events(limit=min(limit, 200))
    return events
