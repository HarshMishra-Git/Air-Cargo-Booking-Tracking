from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    BOOKED = "BOOKED"
    DEPARTED = "DEPARTED"
    ARRIVED = "ARRIVED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class EventType(str, Enum):
    BOOKED = "BOOKED"
    DEPARTED = "DEPARTED"
    ARRIVED = "ARRIVED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class BookingCreate(BaseModel):
    origin: str = Field(..., min_length=3, max_length=10, description="Origin airport code")
    destination: str = Field(..., min_length=3, max_length=10, description="Destination airport code")
    pieces: int = Field(..., gt=0, description="Number of pieces")
    weight_kg: int = Field(..., gt=0, description="Total weight in kg")
    flight_ids: Optional[List[int]] = Field(default=None, description="Optional flight IDs")
    
    @field_validator('origin', 'destination')
    @classmethod
    def validate_airport_code(cls, v: str) -> str:
        return v.upper().strip()


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    flight_ids: Optional[List[int]] = None


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class BookingDepartRequest(BaseModel):
    location: str = Field(..., min_length=3, max_length=10, description="Departure location")
    flight_id: Optional[int] = Field(None, description="Optional flight ID")
    flight_number: Optional[str] = Field(None, max_length=20, description="Optional flight number")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: str) -> str:
        return v.upper().strip()


class BookingArriveRequest(BaseModel):
    location: str = Field(..., min_length=3, max_length=10, description="Arrival location")
    flight_id: Optional[int] = Field(None, description="Optional flight ID")
    flight_number: Optional[str] = Field(None, max_length=20, description="Optional flight number")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: str) -> str:
        return v.upper().strip()


class BookingDeliverRequest(BaseModel):
    location: str = Field(..., min_length=3, max_length=10, description="Delivery location")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: str) -> str:
        return v.upper().strip()


class BookingResponse(BaseModel):
    id: int
    ref_id: str
    origin: str
    destination: str
    pieces: int
    weight_kg: int
    status: BookingStatus
    flight_ids: List[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class BookingEventResponse(BaseModel):
    id: int
    event_type: EventType
    location: Optional[str] = None
    flight_id: Optional[int] = None
    flight_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class BookingHistoryResponse(BaseModel):
    booking: BookingResponse
    timeline: List[BookingEventResponse]
    
    model_config = {"from_attributes": True}