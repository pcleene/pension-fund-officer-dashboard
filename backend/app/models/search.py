"""
Pydantic models for search requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SearchRequest(BaseModel):
    """Text search request model."""
    search_text: Optional[str] = Field(None, alias="searchText")
    filters: Optional[Dict[str, Any]] = None
    limit: int = 20
    cursor: Optional[str] = None
    direction: str = "next"  # "next" or "prev"
    use_facets: bool = True

    model_config = {"populate_by_name": True}


class VectorSearchRequest(BaseModel):
    """Natural language vector search request."""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 20
    num_candidates: int = 100

    model_config = {"populate_by_name": True}


class SearchFilters(BaseModel):
    """Common search filters for members and employers."""
    # Member filters
    account_status: Optional[List[str]] = Field(None, alias="accountStatus")
    region: Optional[List[str]] = None
    generation: Optional[List[str]] = None
    job_category: Optional[List[str]] = Field(None, alias="jobCategory")
    risk_score: Optional[List[str]] = Field(None, alias="riskScore")
    employment_status: Optional[List[str]] = Field(None, alias="employmentStatus")

    # Employer filters
    sector: Optional[List[str]] = None
    company_size: Optional[List[str]] = Field(None, alias="companySize")
    state: Optional[List[str]] = None
    account_type: Optional[List[str]] = Field(None, alias="accountType")
    risk_rating: Optional[List[str]] = Field(None, alias="riskRating")
    has_arrears: Optional[bool] = Field(None, alias="hasArrears")
    has_legal_cases: Optional[bool] = Field(None, alias="hasLegalCases")

    # Common filters
    min_balance: Optional[float] = Field(None, alias="minBalance")
    max_balance: Optional[float] = Field(None, alias="maxBalance")

    model_config = {"populate_by_name": True}


class PaginationInfo(BaseModel):
    """Pagination information in search results."""
    limit: int
    has_more: bool = Field(..., alias="hasMore")
    next_cursor: Optional[str] = Field(None, alias="nextCursor")
    prev_cursor: Optional[str] = Field(None, alias="prevCursor")
    total_count: Optional[int] = Field(None, alias="totalCount")
    current_page_size: int = Field(..., alias="currentPageSize")

    model_config = {"populate_by_name": True}


class FacetBucket(BaseModel):
    """Individual facet bucket with value and count."""
    value: str
    count: int


class Facet(BaseModel):
    """Facet definition for filtering UI."""
    field: str
    field_key: str = Field(..., alias="fieldKey")
    buckets: List[FacetBucket]

    model_config = {"populate_by_name": True}


class SearchResponse(BaseModel):
    """Generic search response."""
    results: List[Any]
    pagination: PaginationInfo
    facets: Optional[List[Facet]] = None
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

    model_config = {"populate_by_name": True}
