"""
In-process async event broker for SSE fan-out.
Supports multiple subscribers, each getting their own queue.
Designed to be replaceable with Redis Pub/Sub for cloud deployment.
"""
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger("agent_waf")


class EventBroker:
    """
    Fan-out event broker: publishes events to all connected SSE clients.
    Each subscriber gets an independent asyncio.Queue.
    """

    def __init__(self):
        self._subscribers: Dict[int, asyncio.Queue] = {}
        self._counter = 0

    def subscribe(self) -> tuple[int, asyncio.Queue]:
        """Register a new subscriber. Returns (subscriber_id, queue)."""
        self._counter += 1
        sub_id = self._counter
        queue = asyncio.Queue(maxsize=100)
        self._subscribers[sub_id] = queue
        logger.debug(f"SSE subscriber {sub_id} connected. Total: {len(self._subscribers)}")
        return sub_id, queue

    def unsubscribe(self, sub_id: int):
        """Remove a subscriber by ID."""
        self._subscribers.pop(sub_id, None)
        logger.debug(f"SSE subscriber {sub_id} disconnected. Total: {len(self._subscribers)}")

    async def publish(self, event: Dict[str, Any]):
        """Fan-out event to all subscribers. Drops events for slow consumers."""
        for sub_id, queue in list(self._subscribers.items()):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # Drop oldest event for slow consumers (backpressure)
                try:
                    queue.get_nowait()
                    queue.put_nowait(event)
                except (asyncio.QueueEmpty, asyncio.QueueFull):
                    pass

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)


# Global broker instance
event_broker = EventBroker()
