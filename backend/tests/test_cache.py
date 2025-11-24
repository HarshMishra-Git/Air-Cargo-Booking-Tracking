import pytest
from unittest.mock import AsyncMock, patch
from app.core.cache import CacheService


@pytest.mark.asyncio
async def test_cache_set_and_get():
    """Test basic cache set and get operations"""
    cache = CacheService()
    cache.redis = AsyncMock()
    
    # Mock Redis responses
    cache.redis.setex = AsyncMock(return_value=True)
    cache.redis.get = AsyncMock(return_value='{"key": "value"}')
    
    # Test set
    result = await cache.set("test_key", {"key": "value"}, ttl=300)
    assert result is True
    cache.redis.setex.assert_called_once()
    
    # Test get
    value = await cache.get("test_key")
    assert value == {"key": "value"}
    cache.redis.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_cache_miss():
    """Test cache miss scenario"""
    cache = CacheService()
    cache.redis = AsyncMock()
    cache.redis.get = AsyncMock(return_value=None)
    
    value = await cache.get("nonexistent_key")
    assert value is None


@pytest.mark.asyncio
async def test_cache_delete():
    """Test cache deletion"""
    cache = CacheService()
    cache.redis = AsyncMock()
    cache.redis.delete = AsyncMock(return_value=1)
    
    result = await cache.delete("test_key")
    assert result is True
    cache.redis.delete.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_cache_delete_pattern():
    """Test pattern-based cache deletion"""
    cache = CacheService()
    cache.redis = AsyncMock()
    
    # Mock scan_iter to return keys
    async def mock_scan_iter(match):
        keys = ["booking:ACB123", "booking:ACB456"]
        for key in keys:
            yield key
    
    cache.redis.scan_iter = mock_scan_iter
    cache.redis.delete = AsyncMock(return_value=2)
    
    deleted = await cache.delete_pattern("booking:*")
    assert deleted == 2


@pytest.mark.asyncio
async def test_cache_exists():
    """Test cache key existence check"""
    cache = CacheService()
    cache.redis = AsyncMock()
    cache.redis.exists = AsyncMock(return_value=1)
    
    exists = await cache.exists("test_key")
    assert exists is True
    
    cache.redis.exists = AsyncMock(return_value=0)
    exists = await cache.exists("nonexistent_key")
    assert exists is False


@pytest.mark.asyncio
async def test_cache_error_handling():
    """Test cache error handling"""
    cache = CacheService()
    cache.redis = AsyncMock()
    cache.redis.get = AsyncMock(side_effect=Exception("Redis error"))
    
    # Should return None on error, not raise
    value = await cache.get("test_key")
    assert value is None
