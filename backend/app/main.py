from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_client import make_asgi_app
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.db import init_db, close_db
from app.core.cache import cache
from app.core.locks import lock_manager
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import bookings_router, routes_router, health_router, metrics_router, auth_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Connect to Redis (cache)
        await cache.connect()
        logger.info("Cache connected")
        
        # Connect to Redis (locks)
        await lock_manager.connect()
        logger.info("Lock manager connected")
        
        # Initialize metrics from database
        from app.core.metrics import initialize_metrics
        await initialize_metrics()
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    
    try:
        await cache.close()
        await lock_manager.close()
        await close_db()
        logger.info("Application shutdown complete")
    
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Air Cargo Booking & Tracking System API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(health_router)
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(bookings_router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_router, prefix=settings.API_V1_PREFIX)
app.include_router(metrics_router)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )