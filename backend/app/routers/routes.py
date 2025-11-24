from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.route_service import RouteService
from app.schemas.route import RouteRequest, RouteResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("/search", response_model=RouteResponse)
async def search_routes(
    route_request: RouteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search for routes between origin and destination
    
    Returns:
    - Direct flights for the given date
    - One-hop transit routes (second hop must be same day or next day)
    """
    
    try:
        service = RouteService(db)
        result = await service.search_routes(route_request)
        return result
    
    except Exception as e:
        logger.error(f"Route search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search routes: {str(e)}"
        )