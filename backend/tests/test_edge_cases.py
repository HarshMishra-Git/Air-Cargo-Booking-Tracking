import pytest
from unittest.mock import AsyncMock, patch
from app.services.booking_service import BookingService
from app.services.route_service import RouteService
from app.schemas.booking import BookingCreate, BookingDepartRequest
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_create_booking_with_zero_pieces(db_session):
    """Test that creating booking with zero pieces fails"""
    service = BookingService(db_session)
    
    with pytest.raises(Exception):  # Pydantic validation error
        BookingCreate(
            origin="DEL",
            destination="BLR",
            pieces=0,  # Invalid
            weight_kg=500
        )


@pytest.mark.asyncio
async def test_create_booking_with_negative_weight(db_session):
    """Test that creating booking with negative weight fails"""
    service = BookingService(db_session)
    
    with pytest.raises(Exception):  # Pydantic validation error
        BookingCreate(
            origin="DEL",
            destination="BLR",
            pieces=10,
            weight_kg=-100  # Invalid
        )


@pytest.mark.asyncio
async def test_create_booking_with_empty_origin(db_session):
    """Test that creating booking with empty origin fails"""
    service = BookingService(db_session)
    
    with pytest.raises(Exception):  # Pydantic validation error
        BookingCreate(
            origin="",  # Invalid
            destination="BLR",
            pieces=10,
            weight_kg=500
        )


@pytest.mark.asyncio
async def test_create_booking_with_very_long_airport_code(db_session):
    """Test that airport codes are validated for length"""
    service = BookingService(db_session)
    
    with pytest.raises(Exception):  # Pydantic validation error
        BookingCreate(
            origin="VERYLONGCODE",  # Too long
            destination="BLR",
            pieces=10,
            weight_kg=500
        )


@pytest.mark.asyncio
async def test_get_nonexistent_booking(db_session):
    """Test getting a booking that doesn't exist"""
    service = BookingService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_booking("NONEXISTENT123")
    
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_depart_nonexistent_booking(db_session):
    """Test departing a booking that doesn't exist"""
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        depart_data = BookingDepartRequest(location="DEL")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.depart_booking("NONEXISTENT123", depart_data)
        
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_route_search_with_past_date(db_session):
    """Test route search with past date (should still work)"""
    from app.schemas.route import RouteRequest
    from datetime import date, timedelta
    
    service = RouteService(db_session)
    
    past_date = (date.today() - timedelta(days=30)).isoformat()
    
    route_request = RouteRequest(
        origin="DEL",
        destination="BLR",
        departure_date=past_date
    )
    
    # Should not raise error, just return empty results
    result = await service.search_routes(route_request)
    assert result.origin == "DEL"
    assert result.destination == "BLR"


@pytest.mark.asyncio
async def test_route_search_same_origin_destination(db_session):
    """Test route search with same origin and destination"""
    from app.schemas.route import RouteRequest
    from datetime import date
    
    service = RouteService(db_session)
    
    route_request = RouteRequest(
        origin="DEL",
        destination="DEL",  # Same as origin
        departure_date=date.today().isoformat()
    )
    
    # Should return empty results
    result = await service.search_routes(route_request)
    assert len(result.direct_flights) == 0
    assert len(result.transit_routes) == 0


@pytest.mark.asyncio
async def test_multiple_rapid_status_updates(db_session, sample_booking_data):
    """Test rapid consecutive status updates"""
    booking_data = BookingCreate(**sample_booking_data)
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        
        # Rapid updates should all succeed due to locking
        depart_data = BookingDepartRequest(location="DEL")
        await service.depart_booking(booking.ref_id, depart_data)
        
        # Immediate second depart should fail
        with pytest.raises(HTTPException):
            await service.depart_booking(booking.ref_id, depart_data)


@pytest.mark.asyncio
async def test_booking_with_special_characters_in_notes(db_session, sample_booking_data):
    """Test booking with special characters in notes"""
    booking_data = BookingCreate(**sample_booking_data)
    service = BookingService(db_session)
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        
        # Depart with special characters
        depart_data = BookingDepartRequest(
            location="DEL",
            notes="Special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
        )
        result = await service.depart_booking(booking.ref_id, depart_data)
        assert result.status == "DEPARTED"


@pytest.mark.asyncio
async def test_booking_with_very_large_weight(db_session):
    """Test booking with very large weight"""
    service = BookingService(db_session)
    
    booking_data = BookingCreate(
        origin="DEL",
        destination="BLR",
        pieces=1,
        weight_kg=999999  # Very large
    )
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        assert booking.weight_kg == 999999


@pytest.mark.asyncio
async def test_booking_with_many_pieces(db_session):
    """Test booking with many pieces"""
    service = BookingService(db_session)
    
    booking_data = BookingCreate(
        origin="DEL",
        destination="BLR",
        pieces=10000,  # Many pieces
        weight_kg=50000
    )
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        assert booking.pieces == 10000


@pytest.mark.asyncio
async def test_lowercase_airport_codes_converted_to_uppercase(db_session):
    """Test that lowercase airport codes are converted to uppercase"""
    service = BookingService(db_session)
    
    booking_data = BookingCreate(
        origin="del",  # lowercase
        destination="blr",  # lowercase
        pieces=10,
        weight_kg=500
    )
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        assert booking.origin == "DEL"
        assert booking.destination == "BLR"


@pytest.mark.asyncio
async def test_whitespace_in_airport_codes_trimmed(db_session):
    """Test that whitespace in airport codes is trimmed"""
    service = BookingService(db_session)
    
    booking_data = BookingCreate(
        origin=" DEL ",  # with whitespace
        destination=" BLR ",  # with whitespace
        pieces=10,
        weight_kg=500
    )
    
    with patch('app.core.locks.lock_manager.lock') as mock_lock:
        mock_lock_instance = AsyncMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=mock_lock_instance)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance
        
        booking = await service.create_booking(booking_data)
        assert booking.origin == "DEL"
        assert booking.destination == "BLR"
