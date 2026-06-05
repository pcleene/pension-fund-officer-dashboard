"""
Employer endpoints for PensionFund Officer Dashboard.
Handles employer search, retrieval, and related operations.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
import logging

from app.database import get_database
from app.models.employers import Employer, EmployerResponse, EmployerSearchResponse
from app.models.search import VectorSearchRequest
from app.services.employer_service import EmployerService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_employer_service():
    """Dependency to get employer service instance."""
    db = await get_database()
    return EmployerService(db)


@router.get("/search", response_model=EmployerSearchResponse)
async def search_employers(
    search_text: Optional[str] = Query(None, description="Text to search in company names, IDs, registration numbers"),
    account_status: Optional[List[str]] = Query(None, description="Filter by account status"),
    sector: Optional[List[str]] = Query(None, description="Filter by industry sector"),
    company_size: Optional[List[str]] = Query(None, description="Filter by company size"),
    state: Optional[List[str]] = Query(None, description="Filter by state"),
    account_type: Optional[List[str]] = Query(None, description="Filter by account type"),
    risk_rating: Optional[List[str]] = Query(None, description="Filter by risk rating"),
    has_arrears: Optional[bool] = Query(None, description="Filter employers with arrears"),
    has_legal_cases: Optional[bool] = Query(None, description="Filter employers with legal cases"),
    product_tags: Optional[List[str]] = Query(None, description="Filter by product tags"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    direction: str = Query("next", pattern="^(next|prev)$", description="Pagination direction"),
    use_facets: bool = Query(True, description="Include facets in response"),
    service: EmployerService = Depends(get_employer_service)
):
    """
    Search employers with full-text search and filtering.

    Supports:
    - Text search across company names, IDs, registration numbers
    - Multi-select filtering on categorical fields
    - Boolean filtering for compliance flags
    - Faceted search for building filter UI
    - Cursor-based pagination
    """
    try:
        filters = {
            "account_status": account_status,
            "sector": sector,
            "company_size": company_size,
            "state": state,
            "account_type": account_type,
            "risk_rating": risk_rating,
            "has_arrears": has_arrears,
            "has_legal_cases": has_legal_cases,
            "product_tags": product_tags
        }

        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        result = await service.search_employers(
            search_text=search_text,
            filters=filters,
            limit=limit,
            cursor=cursor,
            direction=direction,
            use_facets=use_facets
        )

        return result

    except Exception as e:
        logger.error(f"Error searching employers: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/search/vector", response_model=EmployerSearchResponse)
async def vector_search_employers(
    request: VectorSearchRequest,
    service: EmployerService = Depends(get_employer_service)
):
    """
    Natural language semantic search for employers.

    Examples:
    - "Companies with late payments in the tech sector"
    - "High-risk employers with arrears over RM 50,000"
    - "Large employers in Selangor with good compliance"
    """
    try:
        result = await service.vector_search_employers(
            query=request.query,
            filters=request.filters or {},
            limit=request.limit,
            num_candidates=request.num_candidates
        )

        return result

    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")


@router.get("/{employer_id}", response_model=EmployerResponse)
async def get_employer(
    employer_id: str,
    service: EmployerService = Depends(get_employer_service)
):
    """
    Get detailed information for a specific employer by employer ID.
    """
    try:
        employer = await service.get_employer_by_id(employer_id)

        if not employer:
            raise HTTPException(status_code=404, detail=f"Employer {employer_id} not found")

        return EmployerResponse(employer=employer)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving employer {employer_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employer: {str(e)}")


@router.get("/{employer_id}/submissions")
async def get_employer_submissions(
    employer_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: EmployerService = Depends(get_employer_service)
):
    """
    Get contribution submission history for a specific employer.
    Paginated results.
    """
    try:
        submissions = await service.get_employer_submissions(
            employer_id=employer_id,
            limit=limit,
            offset=offset
        )

        return {
            "employer_id": employer_id,
            "submissions": submissions,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error retrieving submissions for {employer_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve submissions: {str(e)}")


@router.get("/{employer_id}/members")
async def get_employer_members(
    employer_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: EmployerService = Depends(get_employer_service)
):
    """
    Get member list for a specific employer.
    Paginated results.
    """
    try:
        members = await service.get_employer_members(
            employer_id=employer_id,
            limit=limit,
            offset=offset
        )

        return {
            "employer_id": employer_id,
            "members": members,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error retrieving members for {employer_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve members: {str(e)}")


@router.get("/{employer_id}/compliance")
async def get_employer_compliance(
    employer_id: str,
    service: EmployerService = Depends(get_employer_service)
):
    """
    Get compliance status and legal case information for an employer.
    """
    try:
        compliance = await service.get_employer_compliance(employer_id)

        return {
            "employer_id": employer_id,
            "compliance": compliance
        }

    except Exception as e:
        logger.error(f"Error retrieving compliance for {employer_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compliance: {str(e)}")
