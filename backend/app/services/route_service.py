from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta
from app.repositories.flight_repository import FlightRepository
from app.schemas.route import RouteRequest, RouteResponse, RouteOption
from app.schemas.flight import FlightResponse
from app.core.cache import cache
from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import route_searches_total, cache_hits_total, cache_misses_total

logger = get_logger(__name__)


class RouteService:
    """Service for route search business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.flight_repo = FlightRepository(db)
    
    async def search_routes(self, route_request: RouteRequest) -> RouteResponse:
        """
        Search for routes between origin and destination
        Returns:
        - Direct flights
        - One-hop transit routes (max 1 stop)
        - Second hop must be same day or next day only
        """
        
        # Update metrics
        route_searches_total.inc()
        
        # Try cache first
        cache_key = f"route:{route_request.origin}:{route_request.destination}:{route_request.departure_date}"
        cached = await cache.get(cache_key)
        if cached:
            cache_hits_total.labels(cache_type='route').inc()
            logger.debug(f"Route cache hit: {cache_key}")
            return RouteResponse(**cached)
        
        cache_misses_total.labels(cache_type='route').inc()
        
        # Search for direct flights
        direct_flights = await self.flight_repo.get_direct_flights(
            origin=route_request.origin,
            destination=route_request.destination,
            departure_date=route_request.departure_date
        )
        
        logger.info(
            f"Found {len(direct_flights)} direct flights from "
            f"{route_request.origin} to {route_request.destination}"
        )
        
        # Search for transit routes (one hop)
        transit_route_pairs = await self.flight_repo.find_transit_routes(
            origin=route_request.origin,
            destination=route_request.destination,
            departure_date=route_request.departure_date
        )
        
        # Process transit routes
        transit_routes = []
        for first_flight, second_flight in transit_route_pairs:
            # Calculate total duration
            total_duration = (
                second_flight.arrival_datetime - first_flight.departure_datetime
            ).total_seconds() / 3600  # Convert to hours
            
            route_option = RouteOption(
                route_type="transit",
                flights=[
                    FlightResponse.model_validate(first_flight),
                    FlightResponse.model_validate(second_flight)
                ],
                total_duration_hours=round(total_duration, 2),
                transit_airport=first_flight.destination
            )
            transit_routes.append(route_option)
        
        logger.info(
            f"Found {len(transit_routes)} transit routes from "
            f"{route_request.origin} to {route_request.destination}"
        )
        
        # Build response
        response = RouteResponse(
            origin=route_request.origin,
            destination=route_request.destination,
            departure_date=route_request.departure_date,
            direct_flights=[FlightResponse.model_validate(f) for f in direct_flights],
            transit_routes=transit_routes
        )
        
        # Cache the result (routes change infrequently)
        await cache.set(cache_key, response.model_dump(), ttl=settings.ROUTE_CACHE_TTL)
        
        return response