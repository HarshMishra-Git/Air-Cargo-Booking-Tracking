from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base


class BookingEvent(Base):
    __tablename__ = "booking_events"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(20), nullable=False)
    location = Column(String(10), nullable=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=True)
    flight_number = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="events")
    
    def __repr__(self):
        return f"<BookingEvent(booking_id={self.booking_id}, type={self.event_type})>"