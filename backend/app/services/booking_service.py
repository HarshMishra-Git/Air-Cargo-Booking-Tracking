from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional
from app.repositories.booking_repository import BookingRepository
from app.repositories.event_repository import EventRepository
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingStatus,
    EventType,
    BookingDepartRequest,
    BookingArriveRequest,
    BookingDeliverRequest,
)
from app.utils.ref_id_generator import generate_unique_ref_id
from app.core.locks import lock_manager
from app.core.cache import cache
from app.core.logging import get_logger
from app.core.metrics import (
    bookings_created_total,
    bookings_departed_total,
    bookings_arrived_total,
    bookings_cancelled_total,
    cache_hits_total,
    cache_misses_total,
)

logger = get_logger(__name__)


class BookingService:
    """Service for booking business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.event_repo = EventRepository(db)
    
    async def create_booking(self, booking_data: BookingCreate) -> BookingResponse:
        """
        Create a new booking
        - Generates unique ref_id
        - Sets initial status to BOOKED
        - Creates initial BOOKED event
        """
        
        # Validate origin and destination are different
        if booking_data.origin == booking_data.destination:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Origin and destination must be different"
            )
        
        # Generate unique ref_id
        existing_ids = await self.booking_repo.get_recent_ref_ids()
        ref_id = generate_unique_ref_id(existing_ids)
        
        # Ensure uniqueness
        max_retries = 10
        for _ in range(max_retries):
            if not await self.booking_repo.ref_id_exists(ref_id):
                break
            ref_id = generate_unique_ref_id(existing_ids)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate unique reference ID"
            )
        
        # Create booking
        booking = await self.booking_repo.create(booking_data, ref_id)
        
        # Create initial BOOKED event
        await self.event_repo.create(
            booking_id=booking.id,
            event_type=EventType.BOOKED,
            location=booking.origin,
            notes="Booking created"
        )
        
        await self.db.commit()
        
        # Update metrics
        bookings_created_total.inc()
        
        logger.info(f"Booking created successfully: {ref_id}")
        
        return BookingResponse.model_validate(booking)
    
    async def depart_booking(
        self,
        ref_id: str,
        depart_data: BookingDepartRequest
    ) -> BookingResponse:
        """
        Mark booking as DEPARTED
        - Uses distributed lock for concurrency control
        - Validates current status
        - Creates DEPARTED event
        """
        
        # Acquire distributed lock
        lock = lock_manager.lock(f"booking:{ref_id}")
        
        try:
            async with lock:
                # Get booking
                booking = await self.booking_repo.get_by_ref_id(ref_id)
                if not booking:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Booking not found: {ref_id}"
                    )
                
                # Validate status transition
                if booking.status == BookingStatus.CANCELLED.value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot depart a cancelled booking"
                    )
                
                if booking.status == BookingStatus.DEPARTED.value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Booking has already departed"
                    )
                
                # Update status
                await self.booking_repo.update_status(booking.id, BookingStatus.DEPARTED)
                
                # Create DEPARTED event
                await self.event_repo.create(
                    booking_id=booking.id,
                    event_type=EventType.DEPARTED,
                    location=depart_data.location,
                    flight_id=depart_data.flight_id,
                    flight_number=depart_data.flight_number,
                    notes=depart_data.notes
                )
                
                await self.db.commit()
                
                # Invalidate cache
                await cache.delete(f"booking:{ref_id}")
                await cache.delete(f"booking_history:{ref_id}")
                
                # Update metrics
                bookings_departed_total.inc()
                
                # Refresh booking
                await self.db.refresh(booking)
                
                logger.info(f"Booking departed: {ref_id} from {depart_data.location}")
                
                return BookingResponse.model_validate(booking)
        
        except TimeoutError:
            logger.error(f"Failed to acquire lock for booking: {ref_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking is being updated by another process. Please try again."
            )
    
    async def arrive_booking(
        self,
        ref_id: str,
        arrive_data: BookingArriveRequest
    ) -> BookingResponse:
        """
        Mark booking as ARRIVED
        - Uses distributed lock for concurrency control
        - Validates current status
        - Creates ARRIVED event
        """
        
        # Acquire distributed lock
        lock = lock_manager.lock(f"booking:{ref_id}")
        
        try:
            async with lock:
                # Get booking
                booking = await self.booking_repo.get_by_ref_id(ref_id)
                if not booking:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Booking not found: {ref_id}"
                    )
                
                # Validate status transition
                if booking.status == BookingStatus.CANCELLED.value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot arrive a cancelled booking"
                    )
                
                if booking.status == BookingStatus.ARRIVED.value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Booking has already arrived"
                    )
                
                # Update status
                await self.booking_repo.update_status(booking.id, BookingStatus.ARRIVED)
                
                # Create ARRIVED event
                await self.event_repo.create(
                    booking_id=booking.id,
                    event_type=EventType.ARRIVED,
                    location=arrive_data.location,
                    flight_id=arrive_data.flight_id,
                    flight_number=arrive_data.flight_number,
                    notes=arrive_data.notes
                )
                
                await self.db.commit()
                
                # Invalidate cache
                await cache.delete(f"booking:{ref_id}")
                await cache.delete(f"booking_history:{ref_id}")
                
                # Update metrics
                bookings_arrived_total.inc()
                
                # Refresh booking
                await self.db.refresh(booking)
                
                logger.info(f"Booking arrived: {ref_id} at {arrive_data.location}")
                
                return BookingResponse.model_validate(booking)
        
        except TimeoutError:
            logger.error(f"Failed to acquire lock for booking: {ref_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking is being updated by another process. Please try again."
            )
    
    async def deliver_booking(
        self,
        ref_id: str,
        deliver_data: BookingDeliverRequest
    ) -> BookingResponse:
        """
        Mark booking as DELIVERED
        - Uses distributed lock for concurrency control
        - Validates current status (must be ARRIVED)
        - Creates DELIVERED event
        """
        
        # Acquire distributed lock
        lock = lock_manager.lock(f"booking:{ref_id}")
        
        try:
            async with lock:
                # Get booking
                booking = await self.booking_repo.get_by_ref_id(ref_id)
                if not booking:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Booking not found: {ref_id}"
                    )
                
                # Validate status transition
                if booking.status == BookingStatus.CANCELLED.value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot deliver a cancelled booking"
                    )
                
                if booking.status == BookingStatus.DELIVERED.value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Booking has already been delivered"
                    )
                
                if booking.status != BookingStatus.ARRIVED.value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Booking must be ARRIVED before it can be delivered"
                    )
                
                # Update status
                await self.booking_repo.update_status(booking.id, BookingStatus.DELIVERED)
                
                # Create DELIVERED event
                await self.event_repo.create(
                    booking_id=booking.id,
                    event_type=EventType.DELIVERED,
                    location=deliver_data.location,
                    notes=deliver_data.notes
                )
                
                await self.db.commit()
                
                # Invalidate cache
                await cache.delete(f"booking:{ref_id}")
                await cache.delete(f"booking_history:{ref_id}")
                
                # Refresh booking
                await self.db.refresh(booking)
                
                logger.info(f"Booking delivered: {ref_id} at {deliver_data.location}")
                
                return BookingResponse.model_validate(booking)
        
        except TimeoutError:
            logger.error(f"Failed to acquire lock for booking: {ref_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking is being updated by another process. Please try again."
            )
    
    async def cancel_booking(self, ref_id: str) -> BookingResponse:
        """
        Cancel a booking
        - Can only cancel if status is not ARRIVED
        - Uses distributed lock for concurrency control
        - Creates CANCELLED event
        """
        
        # Acquire distributed lock
        lock = lock_manager.lock(f"booking:{ref_id}")
        
        try:
            async with lock:
                # Get booking
                booking = await self.booking_repo.get_by_ref_id(ref_id)
                if not booking:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Booking not found: {ref_id}"
                    )
                
                # Validate cancellation is allowed
                if booking.status == BookingStatus.ARRIVED.value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot cancel a booking that has already arrived"
                    )
                
                if booking.status == BookingStatus.CANCELLED.value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Booking is already cancelled"
                    )
                
                # Update status
                await self.booking_repo.update_status(booking.id, BookingStatus.CANCELLED)
                
                # Create CANCELLED event
                await self.event_repo.create(
                    booking_id=booking.id,
                    event_type=EventType.CANCELLED,
                    notes="Booking cancelled by user"
                )
                
                await self.db.commit()
                
                # Invalidate cache
                await cache.delete(f"booking:{ref_id}")
                await cache.delete(f"booking_history:{ref_id}")
                
                # Update metrics
                bookings_cancelled_total.inc()
                
                # Refresh booking
                await self.db.refresh(booking)
                
                logger.info(f"Booking cancelled: {ref_id}")
                
                return BookingResponse.model_validate(booking)
        
        except TimeoutError:
            logger.error(f"Failed to acquire lock for booking: {ref_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking is being updated by another process. Please try again."
            )
    
    async def get_booking(self, ref_id: str) -> BookingResponse:
        """Get booking by reference ID with caching"""
        
        # Try cache first
        cache_key = f"booking:{ref_id}"
        cached = await cache.get(cache_key)
        if cached:
            cache_hits_total.labels(cache_type='booking').inc()
            logger.debug(f"Booking cache hit: {ref_id}")
            return BookingResponse(**cached)
        
        cache_misses_total.labels(cache_type='booking').inc()
        
        # Get from database
        booking = await self.booking_repo.get_by_ref_id(ref_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking not found: {ref_id}"
            )
        
        response = BookingResponse.model_validate(booking)
        
        # Cache the result
        await cache.set(cache_key, response.model_dump(), ttl=300)
        
        return response
    
    async def list_bookings(self, limit: int = 50, offset: int = 0) -> list[BookingResponse]:
        """List recent bookings"""
        bookings = await self.booking_repo.list_bookings(limit, offset)
        return [BookingResponse.model_validate(b) for b in bookings]