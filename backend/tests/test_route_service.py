import pytest
from datetime import datetime, timedelta, date
from app.services.route_service import RouteService
from app.schemas.route import RouteRequest
from app.models.flight import Flight


@pytest.mark.asyncio
async def test_search_direct_routes(db_session):
    """Test searching for direct routes"""
    
    # Create test flights
    departure_date = date.today() + timedelta(days=1)
    departure_datetime = datetime.combine(departure_date, datetime.min.time()) + timedelta(hours=10)
    
    flight = Flight(
        flight_number="AI101",
        airline_name="Air India",
        departure_datetime=departure_datetime,
        arrival_datetime=departure_datetime + timedelta(hours=3),
        origin="DEL",
        destination="BLR"
    )
    
    db_session.add(flight)
    await db_session.commit()
    
    # Search routes
    service = RouteService(db_session)
    route_request = RouteRequest(
        origin="DEL",
        destination="BLR",
        departure_date=departure_date
    )
    
    with patch('app.core.cache.cache.get', return_value=None):
        with patch('app.core.cache.cache.set', return_value=True):
            result = await service.search_routes(route_request)
    
    assert len(result.direct_flights) == 1
    assert result.direct_flights[0].flight_number == "AI101"


@pytest.mark.asyncio
async def test_search_transit_routes(db_session):
    """Test searching for transit routes"""
    
    departure_date = date.today() + timedelta(days=1)
    base_time = datetime.combine(departure_date, datetime.min.time()) + timedelta(hours=10)
    
    # First leg: DEL -> HYD
    flight1 = Flight(
        flight_number="AI201",
        airline_name="Air India",
        departure_datetime=base_time,
        arrival_datetime=base_time + timedelta(hours=2),
        origin="DEL",
        destination="HYD"
    )
    
    # Second leg: HYD -> BLR (same day, after first flight)
    flight2 = Flight(
        flight_number="AI202",
        airline_name="Air India",
        departure_datetime=base_time + timedelta(hours=4),  # 2 hour layover
        arrival_datetime=base_time + timedelta(hours=5),
        origin="HYD",
        destination="BLR"
    )
    
    db_session.add_all([flight1, flight2])
    await db_session.commit()
    
    # Search routes
    service = RouteService(db_session)
    route_request = RouteRequest(
        origin="DEL",
        destination="BLR",
        departure_date=departure_date
    )
    
    with patch('app.core.cache.cache.get', return_value=None):
        with patch('app.core.cache.cache.set', return_value=True):
            result = await service.search_routes(route_request)
    
    assert len(result.transit_routes) >= 1
    assert result.transit_routes[0].transit_airport == "HYD"
    assert len(result.transit_routes[0].flights) == 2


from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_route_search_with_cache_hit(db_session):
    """Test route search with cache hit"""
    route_request = RouteRequest(
        origin="DEL",
        destination="BLR",
        departure_date=date(2025, 12, 1)
    )
    
    cached_response = {
        "origin": "DEL",
        "destination": "BLR",
        "departure_date": "2025-12-01",
        "direct_flights": [],
        "transit_routes": []
    }
    
    with patch('app.core.cache.cache.get', return_value=cached_response):
        service = RouteService(db_session)
        result = await service.search_routes(route_request)
        
        assert result.origin == "DEL"
        assert result.destination == "BLR"


@pytest.mark.asyncio
async def test_transit_route_next_day_constraint(db_session):
    """Test that transit routes respect next day constraint"""
    route_request = RouteRequest(
        origin="DEL",
        destination="BLR",
        departure_date=date(2025, 12, 1)
    )
    
    # Mock first leg flight
    first_flight = MagicMock(spec=Flight)
    first_flight.id = 1
    first_flight.flight_number = "AI101"
    first_flight.airline_name = "Air India"
    first_flight.origin = "DEL"
    first_flight.destination = "HYD"
    first_flight.departure_datetime = datetime(2025, 12, 1, 6, 0)
    first_flight.arrival_datetime = datetime(2025, 12, 1, 9, 0)
    
    # Mock second leg flight (next day)
    second_flight = MagicMock(spec=Flight)
    second_flight.id = 2
    second_flight.flight_number = "AI102"
    second_flight.airline_name = "Air India"
    second_flight.origin = "HYD"
    second_flight.destination = "BLR"
    second_flight.departure_datetime = datetime(2025, 12, 2, 10, 0)
    second_flight.arrival_datetime = datetime(2025, 12, 2, 11, 30)
    
    with patch('app.core.cache.cache.get', return_value=None), \
         patch('app.core.cache.cache.set', return_value=True):
        
        service = RouteService(db_session)
        service.flight_repo.get_direct_flights = AsyncMock(return_value=[])
        service.flight_repo.find_transit_routes = AsyncMock(
            return_value=[(first_flight, second_flight)]
        )
        
        result = await service.search_routes(route_request)
        
        assert len(result.transit_routes) == 1
        assert result.transit_routes[0].transit_airport == "HYD"


@pytest.mark.asyncio
async def test_route_search_cache_miss(db_session):
    """Test route search with cache miss"""
    route_request = RouteRequest(
        origin="DEL",
        destination="BLR",
        departure_date=date(2025, 12, 1)
    )
    
    with patch('app.core.cache.cache.get', return_value=None) as mock_get, \
         patch('app.core.cache.cache.set', return_value=True) as mock_set:
        
        service = RouteService(db_session)
        service.flight_repo.get_direct_flights = AsyncMock(return_value=[])
        service.flight_repo.find_transit_routes = AsyncMock(return_value=[])
        
        result = await service.search_routes(route_request)
        
        # Should call cache.get and cache.set
        mock_get.assert_called_once()
        mock_set.assert_called_once()