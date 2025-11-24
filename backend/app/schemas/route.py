from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
from app.schemas.flight import FlightResponse


class RouteRequest(BaseModel):
    origin: str
    destination: str
    departure_date: date


class RouteOption(BaseModel):
    route_type: str
    flights: List[FlightResponse]
    total_duration_hours: float
    transit_airport: Optional[str] = None


class RouteResponse(BaseModel):
    origin: str
    destination: str
    departure_date: date
    direct_flights: List[FlightResponse]
    transit_routes: List[RouteOption]