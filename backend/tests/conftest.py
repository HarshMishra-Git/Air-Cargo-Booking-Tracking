import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.db import Base
from app.models.booking import Booking
from app.models.flight import Flight
from app.models.booking_event import BookingEvent


# Test database URL - Use local test database
import os
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/aircargo_test"
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
        # Clean up all data after each test
        await session.execute(Base.metadata.tables['booking_events'].delete())
        await session.execute(Base.metadata.tables['bookings'].delete())
        await session.commit()


@pytest.fixture
def sample_booking_data():
    """Sample booking data for tests"""
    return {
        "origin": "DEL",
        "destination": "BLR",
        "pieces": 10,
        "weight_kg": 500
    }


@pytest.fixture
def sample_flight_data():
    """Sample flight data for tests"""
    from datetime import datetime, timedelta, timezone
    
    now = datetime.now(timezone.utc)
    
    return {
        "flight_number": "AI101",
        "airline_name": "Air India",
        "departure_datetime": now + timedelta(hours=2),
        "arrival_datetime": now + timedelta(hours=5),
        "origin": "DEL",
        "destination": "BLR"
    }


@pytest.fixture(autouse=True)
async def setup_redis():
    """Setup Redis connection for tests"""
    from app.core.cache import cache
    from app.core.locks import lock_manager
    
    # Connect to Redis
    try:
        await cache.connect()
        await lock_manager.connect()
    except Exception as e:
        print(f"Warning: Redis not available: {e}")
    
    yield
    
    # Cleanup after tests
    try:
        await cache.close()
        await lock_manager.close()
    except:
        pass