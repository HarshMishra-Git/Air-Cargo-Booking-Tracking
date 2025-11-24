import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.booking_service import BookingService
from app.schemas.booking import BookingCreate, BookingDepartRequest, BookingArriveRequest, BookingStatus
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_create_booking(db_session, sample_booking_data):
    """Test creating a new booking"""
    
    booking_data = BookingCreate(**sample_booking_data)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock_manager:
        service = BookingService(db_session)
        result = await service.create_booking(booking_data)
    
    assert result.ref_id.startswith("ACB")
    assert result.origin == "DEL"
    assert result.destination == "BLR"
    assert result.status == "BOOKED"
    assert result.pieces == 10
    assert result.weight_kg == 500


@pytest.mark.asyncio
async def test_create_booking_same_origin_destination(db_session):
    """Test that booking with same origin and destination fails"""
    
    booking_data = BookingCreate(
        origin="DEL",
        destination="DEL",  # Same as origin
        pieces=10,
        weight_kg=500
    )
    
    service = BookingService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.create_booking(booking_data)
    
    assert exc_info.value.status_code == 400
    assert "different" in str(exc_info.value.detail).lower()


@pytest.mark.asyncio
async def test_depart_booking(db_session, sample_booking_data):
    """Test departing a booking"""
    
    # Create booking first
    booking_data = BookingCreate(**sample_booking_data)
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        
        # Depart the booking
        depart_data = BookingDepartRequest(
            location="DEL",
            flight_number="AI101",
            notes="Departed on time"
        )
        
        result = await service.depart_booking(booking.ref_id, depart_data)
    
    assert result.status == "DEPARTED"
    assert result.ref_id == booking.ref_id


@pytest.mark.asyncio
async def test_arrive_booking(db_session, sample_booking_data):
    """Test arriving a booking"""
    
    booking_data = BookingCreate(**sample_booking_data)
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        
        # Arrive the booking
        arrive_data = BookingArriveRequest(
            location="BLR",
            flight_number="AI101",
            notes="Arrived safely"
        )
        
        result = await service.arrive_booking(booking.ref_id, arrive_data)
    
    assert result.status == "ARRIVED"


@pytest.mark.asyncio
async def test_cancel_booking(db_session, sample_booking_data):
    """Test cancelling a booking"""
    
    booking_data = BookingCreate(**sample_booking_data)
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        result = await service.cancel_booking(booking.ref_id)
    
    assert result.status == "CANCELLED"


@pytest.mark.asyncio
async def test_cancel_arrived_booking_fails(db_session, sample_booking_data):
    """Test that cancelling an arrived booking fails"""
    
    booking_data = BookingCreate(**sample_booking_data)
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        
        # Arrive the booking
        arrive_data = BookingArriveRequest(location="BLR")
        await service.arrive_booking(booking.ref_id, arrive_data)
        
        # Try to cancel - should fail
        with pytest.raises(HTTPException) as exc_info:
            await service.cancel_booking(booking.ref_id)
        
        assert exc_info.value.status_code == 400
        assert "arrived" in str(exc_info.value.detail).lower()


@pytest.mark.asyncio
async def test_get_booking_with_cache(db_session, sample_booking_data):
    """Test getting booking with cache hit"""
    booking_data = BookingCreate(**sample_booking_data)
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock, \
         patch('app.core.cache.cache.get') as mock_cache_get, \
         patch('app.core.cache.cache.set') as mock_cache_set:
        
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        # Create booking
        booking = await service.create_booking(booking_data)
        
        # Mock cache hit
        mock_cache_get.return_value = {
            "id": booking.id,
            "ref_id": booking.ref_id,
            "origin": booking.origin,
            "destination": booking.destination,
            "pieces": booking.pieces,
            "weight_kg": booking.weight_kg,
            "status": booking.status,
            "flight_ids": booking.flight_ids,
            "created_at": booking.created_at.isoformat(),
            "updated_at": booking.updated_at.isoformat()
        }
        
        # Get booking (should hit cache)
        result = await service.get_booking(booking.ref_id)
        assert result.ref_id == booking.ref_id
        mock_cache_get.assert_called_once()


@pytest.mark.asyncio
async def test_depart_cancelled_booking_fails(db_session, sample_booking_data):
    """Test that departing a cancelled booking fails"""
    booking_data = BookingCreate(**sample_booking_data)
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        await service.cancel_booking(booking.ref_id)
        
        # Try to depart - should fail
        depart_data = BookingDepartRequest(location="DEL")
        with pytest.raises(HTTPException) as exc_info:
            await service.depart_booking(booking.ref_id, depart_data)
        
        assert exc_info.value.status_code == 400
        assert "cancelled" in str(exc_info.value.detail).lower()


@pytest.mark.asyncio
async def test_double_depart_fails(db_session, sample_booking_data):
    """Test that departing twice fails"""
    booking_data = BookingCreate(**sample_booking_data)
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        
        depart_data = BookingDepartRequest(location="DEL")
        await service.depart_booking(booking.ref_id, depart_data)
        
        # Try to depart again - should fail
        with pytest.raises(HTTPException) as exc_info:
            await service.depart_booking(booking.ref_id, depart_data)
        
        assert exc_info.value.status_code == 400
        assert "already departed" in str(exc_info.value.detail).lower()