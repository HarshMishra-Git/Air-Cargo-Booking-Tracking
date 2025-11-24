from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.db import get_db
from app.core.cache import cache
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with database and Redis status"""
    
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        if cache.redis:
            await cache.redis.ping()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "not_connected"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["checks"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status