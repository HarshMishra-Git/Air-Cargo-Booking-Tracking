from sqlalchemy import Column, Integer, String, DateTime, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    ref_id = Column(String(20), unique=True, nullable=False, index=True)
    origin = Column(String(10), nullable=False)
    destination = Column(String(10), nullable=False)
    pieces = Column(Integer, nullable=False)
    weight_kg = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="BOOKED", index=True)
    flight_ids = Column(ARRAY(Integer), default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    events = relationship("BookingEvent", back_populates="booking", cascade="all, delete-orphan", lazy="selectin")
    
    def __repr__(self):
        return f"<Booking(ref_id={self.ref_id}, status={self.status})>"