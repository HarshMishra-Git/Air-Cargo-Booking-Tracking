from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class BookingRepository:
    """Repository for booking database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, booking_data: BookingCreate, ref_id: str) -> Booking:
        """Create a new booking"""
        booking = Booking(
            ref_id=ref_id,
            origin=booking_data.origin,
            destination=booking_data.destination,
            pieces=booking_data.pieces,
            weight_kg=booking_data.weight_kg,
            status=BookingStatus.BOOKED.value,
            flight_ids=booking_data.flight_ids or []
        )
        
        self.db.add(booking)
        await self.db.flush()
        await self.db.refresh(booking)
        
        logger.info(f"Booking created: {ref_id}")
        return booking
    
    async def get_by_ref_id(self, ref_id: str) -> Optional[Booking]:
        """Get booking by reference ID"""
        result = await self.db.execute(
            select(Booking).where(Booking.ref_id == ref_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID"""
        result = await self.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()
    
    async def update_status(self, booking_id: int, status: BookingStatus) -> bool:
        """Update booking status"""
        result = await self.db.execute(
            update(Booking)
            .where(Booking.id == booking_id)
            .values(status=status.value)
        )
        
        success = result.rowcount > 0
        if success:
            logger.info(f"Booking {booking_id} status updated to {status.value}")
        return success
    
    async def update_flight_ids(self, booking_id: int, flight_ids: List[int]) -> bool:
        """Update flight IDs"""
        result = await self.db.execute(
            update(Booking)
            .where(Booking.id == booking_id)
            .values(flight_ids=flight_ids)
        )
        
        return result.rowcount > 0
    
    async def ref_id_exists(self, ref_id: str) -> bool:
        """Check if reference ID exists"""
        result = await self.db.execute(
            select(Booking.id).where(Booking.ref_id == ref_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_recent_ref_ids(self, limit: int = 1000) -> set:
        """Get recent reference IDs for collision check"""
        result = await self.db.execute(
            select(Booking.ref_id)
            .order_by(Booking.created_at.desc())
            .limit(limit)
        )
        return {row[0] for row in result.fetchall()}
    
    async def list_bookings(self, limit: int = 50, offset: int = 0) -> List[Booking]:
        """List recent bookings"""
        result = await self.db.execute(
            select(Booking)
            .order_by(Booking.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()