import pytest
import asyncio
import os

# MUST be set before config/main are imported by any tests
os.environ["MONGODB_DATABASE"] = "aivar_waf_test"

# Setup default loop scope for pytest-asyncio to avoid DeprecationWarnings
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def clean_test_database():
    """Ensure the policies collection is empty before each test."""
    from config import settings
    from motor.motor_asyncio import AsyncIOMotorClient
    
    # Safety check
    if not settings.mongodb_database.endswith("_test"):
        raise RuntimeError("Running tests against non-test database!")
        
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    await db.policies.delete_many({})
    
    yield
    client.close()
