from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.db import Base


class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(20), nullable=False)
    airline_name = Column(String(100), nullable=False)
    departure_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    arrival_datetime = Column(DateTime(timezone=True), nullable=False)
    origin = Column(String(10), nullable=False, index=True)
    destination = Column(String(10), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Flight(flight_number={self.flight_number}, route={self.origin}-{self.destination})>"