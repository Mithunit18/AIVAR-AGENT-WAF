"""
Audit repository — writes and queries audit events in MongoDB.
Handles index creation, pagination, filtering, and aggregation.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("agent_waf")


class AuditRepository:
    """Manages audit_logs collection in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["audit_logs"]

    async def write_event(self, event: Dict[str, Any]):
        """Insert an audit event."""
        # Convert datetime objects to ISO strings for consistent serialization
        if isinstance(event.get("timestamp"), datetime):
            event["timestamp"] = event["timestamp"].isoformat()
        await self.collection.insert_one(event)
        logger.debug(f"audit_written event_id={event.get('event_id')}")

    async def get_events(
        self,
        agent_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        decision: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Query audit events with filters and pagination.
        Returns (events, total_count).
        """
        query: Dict[str, Any] = {}
        if agent_id:
            query["agent_id"] = agent_id
        if tool_name:
            query["tool_name"] = tool_name
        if decision:
            query["final_disposition"] = decision
        if start_time or end_time:
            ts_query: Dict[str, str] = {}
            if start_time:
                ts_query["$gte"] = start_time
            if end_time:
                ts_query["$lte"] = end_time
            query["timestamp"] = ts_query

        total = await self.collection.count_documents(query)
        cursor = (
            self.collection.find(query)
            .sort("timestamp", -1)
            .skip(offset)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)

        # Clean _id for serialization
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])

        return docs, total

    async def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single event by event_id."""
        doc = await self.collection.find_one({"event_id": event_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def get_summary(self) -> Dict[str, Any]:
        """Aggregate stats: total, allowed, blocked, block rate, by_rule."""
        pipeline = [
            {
                "$facet": {
                    "total": [{"$count": "count"}],
                    "by_disposition": [
                        {"$group": {"_id": "$final_disposition", "count": {"$sum": 1}}}
                    ],
                    "by_rule": [
                        {"$unwind": "$rule_evaluations"},
                        {"$match": {"rule_evaluations.status": "FAIL"}},
                        {
                            "$group": {
                                "_id": "$rule_evaluations.rule",
                                "count": {"$sum": 1},
                            }
                        },
                    ],
                }
            }
        ]
        result = await self.collection.aggregate(pipeline).to_list(length=1)

        if not result:
            return {"total": 0, "allowed": 0, "blocked": 0, "block_rate": 0.0, "by_rule": {}}

        facets = result[0]
        total = facets["total"][0]["count"] if facets["total"] else 0
        allowed = 0
        blocked = 0
        for item in facets["by_disposition"]:
            if item["_id"] == "ALLOW":
                allowed = item["count"]
            elif item["_id"] == "BLOCK":
                blocked = item["count"]

        by_rule = {item["_id"]: item["count"] for item in facets["by_rule"]}
        block_rate = (blocked / total * 100) if total > 0 else 0.0

        return {
            "total": total,
            "allowed": allowed,
            "blocked": blocked,
            "block_rate": round(block_rate, 2),
            "by_rule": by_rule,
        }

    async def create_indexes(self):
        """Create indexes for common query patterns."""
        await self.collection.create_index("event_id", unique=True)
        await self.collection.create_index("agent_id")
        await self.collection.create_index("session_id")
        await self.collection.create_index("timestamp")
        await self.collection.create_index("tool_name")
        await self.collection.create_index("final_disposition")
        await self.collection.create_index([("agent_id", 1), ("timestamp", -1)])
        await self.collection.create_index([("final_disposition", 1), ("timestamp", -1)])
        logger.info("audit_indexes_created")
