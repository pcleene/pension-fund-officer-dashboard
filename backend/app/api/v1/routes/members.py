"""
Member endpoints for PensionFund Officer Dashboard.
Handles member search, retrieval, and related operations.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
import logging

from app.database import get_database
from app.models.members import Member, MemberResponse, MemberSearchResponse
from app.models.search import SearchRequest, VectorSearchRequest, PaginationInfo
from app.services.member_service import MemberService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_member_service():
    """Dependency to get member service instance."""
    db = await get_database()
    return MemberService(db)


@router.get("/search", response_model=MemberSearchResponse)
async def search_members(
    search_text: Optional[str] = Query(None, description="Text to search in member names, IDs, IC numbers"),
    account_status: Optional[List[str]] = Query(None, description="Filter by account status"),
    region: Optional[List[str]] = Query(None, description="Filter by region"),
    generation: Optional[List[str]] = Query(None, description="Filter by generation group"),
    job_category: Optional[List[str]] = Query(None, description="Filter by job category"),
    risk_score: Optional[List[str]] = Query(None, description="Filter by risk score"),
    employment_status: Optional[List[str]] = Query(None, description="Filter by employment status"),
    min_balance: Optional[float] = Query(None, description="Minimum total balance"),
    max_balance: Optional[float] = Query(None, description="Maximum total balance"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    direction: str = Query("next", pattern="^(next|prev)$", description="Pagination direction"),
    use_facets: bool = Query(True, description="Include facets in response"),
    service: MemberService = Depends(get_member_service)
):
    """
    Search members with full-text search and filtering.

    Supports:
    - Text search across names, IDs, IC numbers
    - Multi-select filtering on categorical fields
    - Range filtering on balance
    - Faceted search for building filter UI
    - Cursor-based pagination
    """
    try:
        filters = {
            "account_status": account_status,
            "region": region,
            "generation": generation,
            "job_category": job_category,
            "risk_score": risk_score,
            "employment_status": employment_status,
            "min_balance": min_balance,
            "max_balance": max_balance
        }

        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        result = await service.search_members(
            search_text=search_text,
            filters=filters,
            limit=limit,
            cursor=cursor,
            direction=direction,
            use_facets=use_facets
        )

        return result

    except Exception as e:
        logger.error(f"Error searching members: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/search/vector", response_model=MemberSearchResponse)
async def vector_search_members(
    request: VectorSearchRequest,
    service: MemberService = Depends(get_member_service)
):
    """
    Natural language semantic search for members.

    Examples:
    - "Show me members with contribution gaps in Kuala Lumpur"
    - "Find high-risk members eligible for housing withdrawal"
    - "Members working in tech sector with incomplete payments"
    """
    try:
        result = await service.vector_search_members(
            query=request.query,
            filters=request.filters or {},
            limit=request.limit,
            num_candidates=request.num_candidates
        )

        return result

    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: str,
    service: MemberService = Depends(get_member_service)
):
    """
    Get detailed information for a specific member by member ID.
    """
    try:
        member = await service.get_member_by_id(member_id)

        if not member:
            raise HTTPException(status_code=404, detail=f"Member {member_id} not found")

        return MemberResponse(member=member)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving member {member_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve member: {str(e)}")


@router.get("/{member_id}/contributions")
async def get_member_contributions(
    member_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: MemberService = Depends(get_member_service)
):
    """
    Get contribution history for a specific member.
    Paginated results.
    """
    try:
        contributions = await service.get_member_contributions(
            member_id=member_id,
            limit=limit,
            offset=offset
        )

        return {
            "member_id": member_id,
            "contributions": contributions,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error retrieving contributions for {member_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve contributions: {str(e)}")


@router.get("/{member_id}/employers")
async def get_member_employers(
    member_id: str,
    service: MemberService = Depends(get_member_service)
):
    """
    Get employer history for a specific member.
    """
    try:
        employers = await service.get_member_employers(member_id)

        return {
            "member_id": member_id,
            "employers": employers
        }

    except Exception as e:
        logger.error(f"Error retrieving employers for {member_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employers: {str(e)}")


@router.get("/{member_id}/withdrawals")
async def get_member_withdrawals(
    member_id: str,
    service: MemberService = Depends(get_member_service)
):
    """
    Get withdrawal history for a specific member.
    """
    try:
        withdrawals = await service.get_member_withdrawals(member_id)

        return {
            "member_id": member_id,
            "withdrawals": withdrawals
        }

    except Exception as e:
        logger.error(f"Error retrieving withdrawals for {member_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve withdrawals: {str(e)}")
