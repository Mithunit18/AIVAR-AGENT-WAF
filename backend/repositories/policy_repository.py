"""
Policy repository — async CRUD with in-memory TTL cache.
MongoDB is the source of truth; cache avoids querying on every request.
"""
import time
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("agent_waf")


class PolicyRepository:
    """
    Manages policy documents in MongoDB with an in-memory cache.
    Cache entries expire after `cache_ttl` seconds.
    """

    def __init__(self, db: AsyncIOMotorDatabase, cache_ttl: int = 30):
        self.collection = db["policies"]
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple[float, Dict[str, Any]]] = {}  # agent_id -> (timestamp, doc)

    def _cache_get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Return cached policy if fresh, else None."""
        entry = self._cache.get(agent_id)
        if entry is None:
            return None
        cached_at, doc = entry
        if time.time() - cached_at > self.cache_ttl:
            del self._cache[agent_id]
            return None
        return doc

    def _cache_set(self, agent_id: str, doc: Dict[str, Any]):
        self._cache[agent_id] = (time.time(), doc)

    def _cache_invalidate(self, agent_id: str):
        self._cache.pop(agent_id, None)

    def _clean_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Remove MongoDB _id for serialization."""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def get_policy(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get policy by agent_id. Uses cache if available."""
        cached = self._cache_get(agent_id)
        if cached is not None:
            logger.debug(f"policy_cache_hit agent_id={agent_id}")
            return cached

        doc = await self.collection.find_one({"agent_id": agent_id})
        if doc:
            doc = self._clean_doc(doc)
            self._cache_set(agent_id, doc)
            logger.debug(f"policy_loaded agent_id={agent_id}")
        return doc

    async def get_all_policies(self) -> List[Dict[str, Any]]:
        """List all policies."""
        cursor = self.collection.find()
        docs = await cursor.to_list(length=1000)
        return [self._clean_doc(d) for d in docs]

    async def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new policy. Raises ValueError if agent_id already exists."""
        agent_id = policy_data["agent_id"]
        existing = await self.collection.find_one({"agent_id": agent_id})
        if existing:
            raise ValueError(f"Policy already exists for agent: {agent_id}")

        now = datetime.now(timezone.utc).isoformat()
        policy_data["version"] = 1
        policy_data["created_at"] = now
        policy_data["updated_at"] = now

        result = await self.collection.insert_one(policy_data)
        policy_data["_id"] = str(result.inserted_id)
        self._cache_set(agent_id, policy_data)
        logger.info(f"policy_created agent_id={agent_id}")
        return policy_data

    async def update_policy(
        self, agent_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update policy fields and increment version."""
        existing = await self.collection.find_one({"agent_id": agent_id})
        if not existing:
            return None

        current_version = existing.get("version", 1)
        updates["version"] = current_version + 1
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        await self.collection.update_one(
            {"agent_id": agent_id}, {"$set": updates}
        )

        self._cache_invalidate(agent_id)
        updated = await self.get_policy(agent_id)
        logger.info(f"policy_updated agent_id={agent_id} version={updates['version']}")
        return updated

    async def delete_policy(self, agent_id: str) -> bool:
        """Delete a policy. Returns True if deleted."""
        result = await self.collection.delete_one({"agent_id": agent_id})
        self._cache_invalidate(agent_id)
        if result.deleted_count > 0:
            logger.info(f"policy_deleted agent_id={agent_id}")
            return True
        return False

    async def create_indexes(self):
        """Create necessary MongoDB indexes."""
        await self.collection.create_index("agent_id", unique=True)
        logger.info("policy_indexes_created")
