import pytest
from unittest.mock import AsyncMock, patch
from app.services.booking_service import BookingService
from app.services.tracking_service import TrackingService
from app.schemas.booking import (
    BookingCreate,
    BookingDepartRequest,
    BookingArriveRequest,
    BookingDeliverRequest
)


@pytest.mark.asyncio
async def test_full_booking_lifecycle(db_session, sample_booking_data):
    """Test complete booking lifecycle: BOOKED -> DEPARTED -> ARRIVED -> DELIVERED"""
    
    booking_data = BookingCreate(**sample_booking_data)
    booking_service = BookingService(db_session)
    tracking_service = TrackingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        # 1. Create booking
        booking = await booking_service.create_booking(booking_data)
        assert booking.status == "BOOKED"
        assert booking.ref_id.startswith("ACB")
        
        # 2. Depart booking
        depart_data = BookingDepartRequest(
            location="DEL",
            flight_number="AI101",
            notes="Departed on time"
        )
        booking = await booking_service.depart_booking(booking.ref_id, depart_data)
        assert booking.status == "DEPARTED"
        
        # 3. Arrive booking
        arrive_data = BookingArriveRequest(
            location="BLR",
            flight_number="AI101",
            notes="Arrived safely"
        )
        booking = await booking_service.arrive_booking(booking.ref_id, arrive_data)
        assert booking.status == "ARRIVED"
        
        # 4. Deliver booking
        deliver_data = BookingDeliverRequest(
            location="BLR",
            notes="Delivered to customer"
        )
        booking = await booking_service.deliver_booking(booking.ref_id, deliver_data)
        assert booking.status == "DELIVERED"
        
        # 5. Check history has all events
        history = await tracking_service.get_booking_history(booking.ref_id)
        assert len(history.timeline) == 4
        assert history.timeline[0].event_type == "BOOKED"
        assert history.timeline[1].event_type == "DEPARTED"
        assert history.timeline[2].event_type == "ARRIVED"
        assert history.timeline[3].event_type == "DELIVERED"


@pytest.mark.asyncio
async def test_booking_cancellation_flow(db_session, sample_booking_data):
    """Test booking cancellation at different stages"""
    
    booking_data = BookingCreate(**sample_booking_data)
    booking_service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        # Cancel immediately after booking
        booking1 = await booking_service.create_booking(booking_data)
        cancelled1 = await booking_service.cancel_booking(booking1.ref_id)
        assert cancelled1.status == "CANCELLED"
        
        # Cancel after departure
        booking2 = await booking_service.create_booking(booking_data)
        depart_data = BookingDepartRequest(location="DEL")
        await booking_service.depart_booking(booking2.ref_id, depart_data)
        cancelled2 = await booking_service.cancel_booking(booking2.ref_id)
        assert cancelled2.status == "CANCELLED"


@pytest.mark.asyncio
async def test_concurrent_status_updates(db_session, sample_booking_data):
    """Test that concurrent updates are handled properly with locks"""
    
    booking_data = BookingCreate(**sample_booking_data)
    booking_service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await booking_service.create_booking(booking_data)
        
        # Simulate concurrent depart operations
        depart_data = BookingDepartRequest(location="DEL")
        result1 = await booking_service.depart_booking(booking.ref_id, depart_data)
        
        # Second depart should fail
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await booking_service.depart_booking(booking.ref_id, depart_data)
        
        assert exc_info.value.status_code == 400
        assert result1.status == "DEPARTED"
