from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.booking_event import BookingEvent
from app.schemas.booking import EventType
from app.core.logging import get_logger

logger = get_logger(__name__)


class EventRepository:
    """Repository for booking event database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        booking_id: int,
        event_type: EventType,
        location: Optional[str] = None,
        flight_id: Optional[int] = None,
        flight_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> BookingEvent:
        """Create a new booking event"""
        
        event = BookingEvent(
            booking_id=booking_id,
            event_type=event_type.value,
            location=location,
            flight_id=flight_id,
            flight_number=flight_number,
            notes=notes
        )
        
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        
        logger.info(f"Event created: {event_type.value} for booking {booking_id}")
        return event
    
    async def get_by_booking_id(self, booking_id: int) -> List[BookingEvent]:
        """Get all events for a booking, ordered chronologically"""
        
        result = await self.db.execute(
            select(BookingEvent)
            .where(BookingEvent.booking_id == booking_id)
            .order_by(BookingEvent.created_at.asc())
        )
        
        return result.scalars().all()