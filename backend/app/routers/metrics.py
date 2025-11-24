from fastapi import APIRouter
from app.core.metrics import (
    bookings_created_total,
    bookings_departed_total,
    bookings_arrived_total,
    bookings_cancelled_total,
    route_searches_total,
    cache_hits_total,
    cache_misses_total,
)

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


@router.get("/summary")
async def get_metrics_summary():
    """Get human-readable metrics summary"""
    try:
        return {
            "bookings": {
                "created": int(bookings_created_total._value._value),
                "departed": int(bookings_departed_total._value._value),
                "arrived": int(bookings_arrived_total._value._value),
                "cancelled": int(bookings_cancelled_total._value._value),
            },
            "routes": {
                "searches": int(route_searches_total._value._value),
            },
            "cache": {
                "hits": 0,
                "misses": 0,
            }
        }
    except Exception as e:
        return {
            "bookings": {"created": 0, "departed": 0, "arrived": 0, "cancelled": 0},
            "routes": {"searches": 0},
            "cache": {"hits": 0, "misses": 0}
        }
