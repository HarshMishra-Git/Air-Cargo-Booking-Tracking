from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.booking_repository import BookingRepository
from app.repositories.event_repository import EventRepository
from app.schemas.booking import BookingHistoryResponse, BookingResponse, BookingEventResponse
from app.core.cache import cache
from app.core.logging import get_logger

logger = get_logger(__name__)


class TrackingService:
    """Service for booking tracking and history"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.event_repo = EventRepository(db)
    
    async def get_booking_history(self, ref_id: str) -> BookingHistoryResponse:
        """
        Get booking with full chronological event timeline
        Used by UI for tracking
        """
        
        # Try cache first
        cache_key = f"booking_history:{ref_id}"
        cached = await cache.get(cache_key)
        if cached:
            logger.debug(f"Booking history cache hit: {ref_id}")
            return BookingHistoryResponse(**cached)
        
        # Get booking
        booking = await self.booking_repo.get_by_ref_id(ref_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking not found: {ref_id}"
            )
        
        # Get all events (chronologically ordered)
        events = await self.event_repo.get_by_booking_id(booking.id)
        
        # Build response
        response = BookingHistoryResponse(
            booking=BookingResponse.model_validate(booking),
            timeline=[BookingEventResponse.model_validate(e) for e in events]
        )
        
        # Cache the result
        await cache.set(cache_key, response.model_dump(), ttl=300)
        
        logger.info(f"Retrieved booking history: {ref_id} with {len(events)} events")
        
        return response