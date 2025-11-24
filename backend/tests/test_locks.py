import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.locks import DistributedLock, LockManager


@pytest.mark.asyncio
async def test_lock_acquisition_success():
    """Test successful lock acquisition"""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=True)
    
    lock = DistributedLock(redis_mock, "test_resource", timeout=10)
    result = await lock.acquire(retry_times=1, retry_delay=0.01)
    
    assert result is True
    assert lock.acquired is True
    redis_mock.set.assert_called_once()


@pytest.mark.asyncio
async def test_lock_acquisition_failure():
    """Test lock acquisition failure after retries"""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=False)
    
    lock = DistributedLock(redis_mock, "test_resource", timeout=10)
    result = await lock.acquire(retry_times=3, retry_delay=0.01)
    
    assert result is False
    assert lock.acquired is False
    assert redis_mock.set.call_count == 3


@pytest.mark.asyncio
async def test_lock_release_success():
    """Test successful lock release"""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.eval = AsyncMock(return_value=1)
    
    lock = DistributedLock(redis_mock, "test_resource", timeout=10)
    await lock.acquire(retry_times=1)
    
    result = await lock.release()
    assert result is True
    assert lock.acquired is False


@pytest.mark.asyncio
async def test_lock_release_not_owned():
    """Test releasing a lock that's not owned"""
    redis_mock = AsyncMock()
    redis_mock.eval = AsyncMock(return_value=0)
    
    lock = DistributedLock(redis_mock, "test_resource", timeout=10)
    lock.acquired = True
    
    result = await lock.release()
    assert result is False


@pytest.mark.asyncio
async def test_lock_context_manager():
    """Test lock as context manager"""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.eval = AsyncMock(return_value=1)
    
    lock = DistributedLock(redis_mock, "test_resource", timeout=10)
    
    async with lock:
        assert lock.acquired is True
    
    assert lock.acquired is False


@pytest.mark.asyncio
async def test_lock_context_manager_timeout():
    """Test lock context manager with timeout"""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=False)
    
    lock = DistributedLock(redis_mock, "test_resource", timeout=10)
    
    with pytest.raises(TimeoutError):
        async with lock:
            pass


@pytest.mark.asyncio
async def test_lock_extend():
    """Test lock extension"""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.eval = AsyncMock(return_value=1)
    
    lock = DistributedLock(redis_mock, "test_resource", timeout=10)
    await lock.acquire()
    
    result = await lock.extend(additional_time=20)
    assert result is True


@pytest.mark.asyncio
async def test_lock_manager_creation():
    """Test lock manager creates locks correctly"""
    manager = LockManager()
    manager.redis = AsyncMock()
    
    lock = manager.lock("test_resource", timeout=15)
    
    assert isinstance(lock, DistributedLock)
    assert lock.resource == "lock:test_resource"
    assert lock.timeout == 15
