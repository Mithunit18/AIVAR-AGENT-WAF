import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "agent_waf"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Application
    waf_env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174"

    # Policy cache TTL (seconds)
    policy_cache_ttl: int = 30

    # Build Versioning
    commit_sha: str = "unknown"

    @property
    def cors_origins_list(self) -> List[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        # Always allow local frontend dev servers regardless of .env overrides
        for local_origin in ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174"]:
            if local_origin not in origins:
                origins.append(local_origin)
        return origins

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
