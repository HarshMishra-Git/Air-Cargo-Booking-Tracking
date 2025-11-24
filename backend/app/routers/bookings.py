from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.booking_service import BookingService
from app.services.tracking_service import TrackingService
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingHistoryResponse,
    BookingDepartRequest,
    BookingArriveRequest,
    BookingDeliverRequest,
)
from typing import List
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new booking
    - Generates unique ref_id (format: ACB12345)
    - Sets initial status to BOOKED
    - Creates initial event in timeline
    """
    
    try:
        service = BookingService(db)
        result = await service.create_booking(booking_data)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Booking creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("", response_model=List[BookingResponse])
async def list_bookings(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List bookings with pagination
    - limit: Number of results (default: 50, max: 100)
    - offset: Number of results to skip (default: 0)
    """
    
    try:
        # Enforce max limit
        limit = min(limit, 100)
        
        from app.repositories.booking_repository import BookingRepository
        repo = BookingRepository(db)
        bookings = await repo.list_bookings(limit=limit, offset=offset)
        
        return [BookingResponse.model_validate(b) for b in bookings]
    
    except Exception as e:
        logger.error(f"List bookings failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list bookings: {str(e)}"
        )


@router.get("/{ref_id}", response_model=BookingResponse)
async def get_booking(
    ref_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get booking details by reference ID"""
    
    try:
        service = BookingService(db)
        result = await service.get_booking(ref_id)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get booking failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get booking: {str(e)}"
        )


@router.post("/{ref_id}/depart", response_model=BookingResponse)
async def depart_booking(
    ref_id: str,
    depart_data: BookingDepartRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark booking as DEPARTED
    - Updates status to DEPARTED
    - Records departure location and optional flight info
    - Creates DEPARTED event in timeline
    - Uses distributed locks to handle concurrent updates
    """
    
    try:
        service = BookingService(db)
        result = await service.depart_booking(ref_id, depart_data)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Booking departure failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to depart booking: {str(e)}"
        )


@router.post("/{ref_id}/arrive", response_model=BookingResponse)
async def arrive_booking(
    ref_id: str,
    arrive_data: BookingArriveRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark booking as ARRIVED
    - Updates status to ARRIVED
    - Records arrival location and optional flight info
    - Creates ARRIVED event in timeline
    - Uses distributed locks to handle concurrent updates
    """
    
    try:
        service = BookingService(db)
        result = await service.arrive_booking(ref_id, arrive_data)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Booking arrival failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to arrive booking: {str(e)}"
        )


@router.post("/{ref_id}/deliver", response_model=BookingResponse)
async def deliver_booking(
    ref_id: str,
    deliver_data: BookingDeliverRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark booking as DELIVERED
    - Only allowed if status is ARRIVED
    - Updates status to DELIVERED
    - Creates DELIVERED event in timeline
    - Uses distributed locks to handle concurrent updates
    """
    
    try:
        service = BookingService(db)
        result = await service.deliver_booking(ref_id, deliver_data)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Booking delivery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deliver booking: {str(e)}"
        )


@router.delete("/{ref_id}", response_model=BookingResponse)
async def cancel_booking(
    ref_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a booking
    - Only allowed if status is not ARRIVED
    - Updates status to CANCELLED
    - Creates CANCELLED event in timeline
    - Uses distributed locks to handle concurrent updates
    """
    
    try:
        service = BookingService(db)
        result = await service.cancel_booking(ref_id)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Booking cancellation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel booking: {str(e)}"
        )


@router.get("/{ref_id}/history", response_model=BookingHistoryResponse)
async def get_booking_history(
    ref_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get booking with full chronological event timeline
    - Returns booking details + all events ordered by time
    - Used by UI for tracking display
    """
    
    try:
        service = TrackingService(db)
        result = await service.get_booking_history(ref_id)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get booking history failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get booking history: {str(e)}"
        )