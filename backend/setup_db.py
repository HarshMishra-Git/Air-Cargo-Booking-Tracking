"""
Database setup script - Run migrations and initialize database
"""
import asyncio
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def setup_database():
    """Setup database with migrations"""
    
    try:
        # Create sync engine for Alembic
        engine = create_engine(settings.DATABASE_URL_SYNC)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        
        logger.info("Database setup complete!")
        logger.info("Run 'alembic upgrade head' to apply migrations")
        
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(setup_database())
    sys.exit(0 if success else 1)
