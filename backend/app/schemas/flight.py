from pydantic import BaseModel
from datetime import datetime


class FlightBase(BaseModel):
    flight_number: str
    airline_name: str
    departure_datetime: datetime
    arrival_datetime: datetime
    origin: str
    destination: str


class FlightResponse(FlightBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}