from prometheus_client import Counter, Histogram, Gauge, Info
import time
from app.core.logging import get_logger

logger = get_logger(__name__)

# Application Info
app_info = Info('aircargo_app', 'Air Cargo Application Info')
app_info.info({'version': '1.0.0', 'environment': 'production'})

# Business Metrics
bookings_created_total = Counter(
    'bookings_created_total',
    'Total number of bookings created'
)

bookings_departed_total = Counter(
    'bookings_departed_total',
    'Total number of bookings marked as departed'
)

bookings_arrived_total = Counter(
    'bookings_arrived_total',
    'Total number of bookings marked as arrived'
)

bookings_cancelled_total = Counter(
    'bookings_cancelled_total',
    'Total number of bookings cancelled'
)

route_searches_total = Counter(
    'route_searches_total',
    'Total number of route searches performed'
)

# Performance Metrics
request_duration_seconds = Histogram(
    'request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint', 'status']
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total number of cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total number of cache misses',
    ['cache_type']
)

# Lock Metrics
lock_acquisitions_total = Counter(
    'lock_acquisitions_total',
    'Total number of successful lock acquisitions'
)

lock_failures_total = Counter(
    'lock_failures_total',
    'Total number of failed lock acquisitions'
)

lock_wait_duration_seconds = Histogram(
    'lock_wait_duration_seconds',
    'Time spent waiting for locks'
)

# Database Metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

# Error Metrics
errors_total = Counter(
    'errors_total',
    'Total number of errors',
    ['error_type', 'endpoint']
)

# Initialize metrics from database
async def initialize_metrics():
    """Load existing counts from database to persist metrics across restarts"""
    try:
        from app.core.db import AsyncSessionLocal
        from sqlalchemy import select, func
        from app.models.booking import Booking
        
        async with AsyncSessionLocal() as db:
            # Total bookings
            result = await db.execute(select(func.count(Booking.id)))
            total = result.scalar() or 0
            bookings_created_total._value.set(total)
            
            # By status
            for status, counter in [
                ('DEPARTED', bookings_departed_total),
                ('ARRIVED', bookings_arrived_total),
                ('CANCELLED', bookings_cancelled_total)
            ]:
                result = await db.execute(
                    select(func.count(Booking.id)).where(Booking.status == status)
                )
                count = result.scalar() or 0
                counter._value.set(count)
            
            logger.info(f"Metrics initialized from database: {total} bookings")
    except Exception as e:
        logger.warning(f"Could not initialize metrics from database: {e}")
