from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Air Cargo Booking System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/aircargo"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@postgres:5432/aircargo"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = '["http://localhost:3000","http://frontend:3000"]'
    
    # Lock Configuration
    LOCK_TIMEOUT: int = 10
    LOCK_RETRY_DELAY: float = 0.1
    LOCK_RETRY_TIMES: int = 50
    
    # Cache Configuration
    CACHE_TTL: int = 300
    ROUTE_CACHE_TTL: int = 3600
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars-long"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @property
    def cors_origins_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError, ValueError):
            return ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()