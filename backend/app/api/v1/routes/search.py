"""
Unified search endpoint for both members and employers.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def unified_search(
    q: str = Query(..., description="Search query"),
    entity_type: Literal["members", "employers", "all"] = Query("all", description="Entity type to search"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Unified search endpoint across members and employers.
    Useful for global search functionality.
    """
    try:
        # TODO: Implement unified search logic
        return {
            "query": q,
            "entity_type": entity_type,
            "limit": limit,
            "message": "Unified search not yet implemented. Use /members/search or /employers/search instead."
        }

    except Exception as e:
        logger.error(f"Error in unified search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
