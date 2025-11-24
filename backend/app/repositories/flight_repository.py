from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List
from datetime import datetime, date, timedelta, timezone
from app.models.flight import Flight
from app.core.logging import get_logger

logger = get_logger(__name__)


class FlightRepository:
    """Repository for flight database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_direct_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date
    ) -> List[Flight]:
        """Get direct flights for a route on a specific date"""
        
        start_datetime = datetime.combine(departure_date, datetime.min.time(), tzinfo=timezone.utc)
        end_datetime = datetime.combine(departure_date, datetime.max.time(), tzinfo=timezone.utc)
        
        result = await self.db.execute(
            select(Flight)
            .where(
                and_(
                    Flight.origin == origin,
                    Flight.destination == destination,
                    Flight.departure_datetime >= start_datetime,
                    Flight.departure_datetime <= end_datetime
                )
            )
            .order_by(Flight.departure_datetime)
        )
        
        flights = result.scalars().all()
        logger.info(f"Query: origin={origin}, dest={destination}, start={start_datetime}, end={end_datetime}")
        logger.info(f"Found {len(flights)} direct flights from {origin} to {destination} on {departure_date}")
        return flights
    
    async def get_flights_from_origin(
        self,
        origin: str,
        departure_date: date
    ) -> List[Flight]:
        """Get all flights departing from origin on a specific date"""
        
        start_datetime = datetime.combine(departure_date, datetime.min.time(), tzinfo=timezone.utc)
        end_datetime = datetime.combine(departure_date, datetime.max.time(), tzinfo=timezone.utc)
        
        result = await self.db.execute(
            select(Flight)
            .where(
                and_(
                    Flight.origin == origin,
                    Flight.departure_datetime >= start_datetime,
                    Flight.departure_datetime <= end_datetime
                )
            )
            .order_by(Flight.departure_datetime)
        )
        
        return result.scalars().all()
    
    async def get_flights_to_destination(
        self,
        destination: str,
        start_datetime: datetime,
        end_datetime: datetime
    ) -> List[Flight]:
        """Get flights arriving at destination within time window"""
        
        result = await self.db.execute(
            select(Flight)
            .where(
                and_(
                    Flight.destination == destination,
                    Flight.departure_datetime >= start_datetime,
                    Flight.departure_datetime <= end_datetime
                )
            )
            .order_by(Flight.departure_datetime)
        )
        
        return result.scalars().all()
    
    async def find_transit_routes(
        self,
        origin: str,
        destination: str,
        departure_date: date
    ) -> List[tuple[Flight, Flight]]:
        """
        Find one-hop transit routes
        Returns list of (first_flight, second_flight) tuples
        """
        
        # Get first leg flights
        first_leg_flights = await self.get_flights_from_origin(origin, departure_date)
        
        transit_routes = []
        
        for first_flight in first_leg_flights:
            # Transit airport is the destination of first flight
            transit_airport = first_flight.destination
            
            # Skip if transit airport is same as final destination
            if transit_airport == destination:
                continue
            
            # Second flight must depart on same day or next day
            # And after first flight arrives (with minimum connection time)
            min_connection_time = timedelta(hours=2)
            earliest_departure = first_flight.arrival_datetime + min_connection_time
            
            # Latest departure is end of next day
            latest_departure = datetime.combine(
                departure_date + timedelta(days=1),
                datetime.max.time(),
                tzinfo=timezone.utc
            )
            
            # Get connecting flights
            second_leg_flights = await self.get_flights_to_destination(
                destination,
                earliest_departure,
                latest_departure
            )
            
            # Filter second leg flights that depart from transit airport
            for second_flight in second_leg_flights:
                if second_flight.origin == transit_airport:
                    transit_routes.append((first_flight, second_flight))
        
        logger.debug(f"Found {len(transit_routes)} transit routes from {origin} to {destination}")
        return transit_routes
    
    async def get_by_id(self, flight_id: int) -> Flight:
        """Get flight by ID"""
        result = await self.db.execute(
            select(Flight).where(Flight.id == flight_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, flight_ids: List[int]) -> List[Flight]:
        """Get multiple flights by IDs"""
        if not flight_ids:
            return []
        
        result = await self.db.execute(
            select(Flight).where(Flight.id.in_(flight_ids))
        )
        return result.scalars().all()