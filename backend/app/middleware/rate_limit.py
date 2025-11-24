from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.cache import cache
from app.core.config import settings
from app.core.logging import get_logger
import time

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/detailed", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = request.client.host
        
        # Create rate limit key
        current_minute = int(time.time() / 60)
        rate_limit_key = f"rate_limit:{client_ip}:{current_minute}"
        
        try:
            # Get current count
            current_count = await cache.redis.get(rate_limit_key)
            
            if current_count is None:
                # First request in this minute
                await cache.redis.setex(rate_limit_key, 60, 1)
            else:
                current_count = int(current_count)
                
                if current_count >= settings.RATE_LIMIT_PER_MINUTE:
                    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later."
                    )
                
                # Increment counter
                await cache.redis.incr(rate_limit_key)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Continue on error to not block requests
        
        response = await call_next(request)
        return response
