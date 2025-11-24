import asyncio
import time
import uuid
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DistributedLock:
    """Redis-based distributed lock using Redlock algorithm"""
    
    def __init__(self, redis_client: aioredis.Redis, resource: str, timeout: int = None):
        self.redis = redis_client
        self.resource = f"lock:{resource}"
        self.timeout = timeout or settings.LOCK_TIMEOUT
        self.lock_id = str(uuid.uuid4())
        self.acquired = False
    
    async def acquire(self, retry_times: int = None, retry_delay: float = None) -> bool:
        """Acquire the distributed lock with retry logic"""
        retry_times = retry_times or settings.LOCK_RETRY_TIMES
        retry_delay = retry_delay or settings.LOCK_RETRY_DELAY
        
        for attempt in range(retry_times):
            try:
                # Try to acquire lock
                result = await self.redis.set(
                    self.resource,
                    self.lock_id,
                    nx=True,  # Only set if not exists
                    ex=self.timeout  # Expiration time
                )
                
                if result:
                    self.acquired = True
                    logger.debug(f"Lock acquired: {self.resource} (attempt {attempt + 1}/{retry_times})")
                    return True
                
                # Lock not acquired, wait before retry
                if attempt < retry_times - 1:
                    await asyncio.sleep(retry_delay)
                    logger.debug(f"Lock acquire retry {attempt + 1}/{retry_times}: {self.resource}")
            
            except Exception as e:
                logger.error(f"Error acquiring lock {self.resource}: {e}")
                if attempt < retry_times - 1:
                    await asyncio.sleep(retry_delay)
        
        logger.warning(f"Failed to acquire lock after {retry_times} attempts: {self.resource}")
        return False
    
    async def release(self) -> bool:
        """Release the distributed lock"""
        if not self.acquired:
            return False
        
        try:
            # Lua script to ensure we only delete our own lock
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            
            result = await self.redis.eval(lua_script, 1, self.resource, self.lock_id)
            
            if result:
                self.acquired = False
                logger.debug(f"Lock released: {self.resource}")
                return True
            else:
                logger.warning(f"Lock not owned or expired: {self.resource}")
                return False
        
        except Exception as e:
            logger.error(f"Error releasing lock {self.resource}: {e}")
            return False
    
    async def extend(self, additional_time: int = None) -> bool:
        """Extend lock expiration"""
        if not self.acquired:
            return False
        
        try:
            additional_time = additional_time or self.timeout
            
            # Lua script to extend lock only if we own it
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("expire", KEYS[1], ARGV[2])
            else
                return 0
            end
            """
            
            result = await self.redis.eval(
                lua_script,
                1,
                self.resource,
                self.lock_id,
                additional_time
            )
            
            if result:
                logger.debug(f"Lock extended: {self.resource} (+{additional_time}s)")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Error extending lock {self.resource}: {e}")
            return False
    
    async def __aenter__(self):
        """Context manager entry"""
        acquired = await self.acquire()
        if not acquired:
            raise TimeoutError(f"Could not acquire lock: {self.resource}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.release()


class LockManager:
    """Manager for distributed locks"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50
            )
            await self.redis.ping()
            logger.info("Lock manager Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect lock manager to Redis: {e}")
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Lock manager Redis connection closed")
    
    def lock(self, resource: str, timeout: int = None) -> DistributedLock:
        """Create a distributed lock"""
        return DistributedLock(self.redis, resource, timeout)


# Global lock manager instance
lock_manager = LockManager()