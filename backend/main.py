"""
Agent WAF — FastAPI Application Entry Point.
Wires together all components: DB, Redis, repositories, tools, routes, middleware.
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis

from config import settings
from middleware import RequestIDMiddleware
from exceptions import register_exception_handlers
from repositories.policy_repository import PolicyRepository
from repositories.audit_repository import AuditRepository
from tools.registry import create_default_registry
from events.broker import event_broker
from routers import proxy, dashboard, policies


# ─── Logging Setup ────────────────────────────────────────────────────────────

def setup_logging():
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
    )
    # Quiet down noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger("agent_waf")


# ─── Default Policy Seed ──────────────────────────────────────────────────────

async def seed_default_policy(policy_repo: PolicyRepository):
    """
    Seed or migrate the default demo policy.
    Ensures idempotency and adds missing required fields to existing policies.
    """
    existing_policies = await policy_repo.get_all_policies()
    
    # 1. Migrate existing policies (add missing fields)
    for p in existing_policies:
        updates = {}
        if "tool_permissions" not in p:
            updates["tool_permissions"] = {}
        if "shadow_mode" not in p:
            updates["shadow_mode"] = False
            
        # Specific migration for support-agent-01
        if p.get("agent_id") == "support-agent-01":
            current_perms = updates.get("tool_permissions", p.get("tool_permissions", {}))
            if "crm_delete" not in current_perms:
                # Create a fresh copy to avoid modifying the reference in a way that breaks updates
                new_perms = dict(current_perms)
                new_perms["crm_delete"] = {"enabled": False}
                updates["tool_permissions"] = new_perms
                
        if updates:
            await policy_repo.update_policy(p["agent_id"], updates)
            logger.info(f"policy_migrated agent_id={p['agent_id']} updates={list(updates.keys())}")
            
    # 2. Create support-agent-01 if it doesn't exist
    has_default = any(p.get("agent_id") == "support-agent-01" for p in existing_policies)
    if not has_default:
        default_policy = {
            "agent_id": "support-agent-01",
            "enabled": True,
            "rate_limit": {
                "enabled": True,
                "max_calls": 5,
                "window_seconds": 60,
            },
            "parameter_validation": {
                "enabled": True,
                "blocked_values": ["delete", "DROP TABLE", "rm -rf"],
                "max_parameter_size": 10000,
            },
            "data_scope": {
                "enabled": True,
                "allowed_scopes": {
                    "customer_id": ["C101", "C102"],
                },
            },
            "sequence_rules": {
                "enabled": True,
                "rules": [
                    {"tool": "crm_update", "requires": "authenticate_user"},
                ],
            },
            "tool_permissions": {
                "crm_delete": {"enabled": False}
            },
            "shadow_mode": False,
        }
        await policy_repo.create_policy(default_policy)
        logger.info("default_policy_seeded agent_id=support-agent-01")
    else:
        logger.info(f"policies_found count={len(existing_policies)}")


# ─── Application Lifespan ────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"agent_waf_starting env={settings.waf_env}")

    # MongoDB
    db_client = AsyncIOMotorClient(settings.mongodb_url)
    db = db_client[settings.mongodb_database]
    app.state.db = db
    app.state.db_client = db_client

    # Redis
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = redis_client

    # Repositories
    policy_repo = PolicyRepository(db, cache_ttl=settings.policy_cache_ttl)
    audit_repo = AuditRepository(db)
    app.state.policy_repo = policy_repo
    app.state.audit_repo = audit_repo

    # Tool Registry
    app.state.tool_registry = create_default_registry()

    # Event Broker
    app.state.event_broker = event_broker

    # Create indexes
    await policy_repo.create_indexes()
    await audit_repo.create_indexes()

    # Seed default policy
    await seed_default_policy(policy_repo)

    logger.info("agent_waf_ready")
    yield

    # Cleanup
    db_client.close()
    await redis_client.aclose()
    logger.info("agent_waf_shutdown")


# ─── App Creation ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agent WAF API",
    description="Policy-enforcing proxy for AI agent tool invocations",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Exception handlers
register_exception_handlers(app)

# Routers
app.include_router(proxy.router, prefix="/api/v1/proxy", tags=["WAF Proxy"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])


# ─── Health & Readiness ──────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health():
    """Liveness probe — confirms the process is running."""
    return {"status": "healthy", "service": "agent-waf", "commit_sha": settings.commit_sha}


@app.get("/ready", tags=["Health"])
async def ready():
    """Readiness probe — checks MongoDB and Redis connectivity."""
    checks = {}

    # MongoDB check
    try:
        await app.state.db.command("ping")
        checks["mongodb"] = "ok"
    except Exception as e:
        checks["mongodb"] = f"error: {str(e)}"

    # Redis check
    try:
        await app.state.redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
    }


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Agent WAF is running", "version": "1.0.0", "commit_sha": settings.commit_sha}
