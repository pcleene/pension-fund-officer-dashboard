"""
Pydantic models for data validation and serialization.
"""
from .members import (
    PersonalInfo,
    EmploymentProfile,
    AccountInfo,
    ContributionRecord,
    ContributionStats,
    EmployerHistory,
    WithdrawalRecord,
    EligibilityFlags,
    ComplianceFlags,
    Metadata,
    Member,
    MemberResponse,
    MemberSearchResponse
)

from .employers import (
    CompanyProfile,
    AccountStatus,
    MemberSummary,
    ContributionSubmission,
    ContributionStatistics,
    ComplianceStatus,
    LegalCase,
    MemberReference,
    Employer,
    EmployerResponse,
    EmployerSearchResponse
)

from .search import (
    SearchRequest,
    VectorSearchRequest,
    SearchFilters,
    PaginationInfo,
    FacetBucket,
    Facet,
    SearchResponse
)

from .dashboard import (
    DashboardStats,
    MemberDashboardStats,
    EmployerDashboardStats
)

__all__ = [
    # Members
    "PersonalInfo",
    "EmploymentProfile",
    "AccountInfo",
    "ContributionRecord",
    "ContributionStats",
    "EmployerHistory",
    "WithdrawalRecord",
    "EligibilityFlags",
    "ComplianceFlags",
    "Metadata",
    "Member",
    "MemberResponse",
    "MemberSearchResponse",
    # Employers
    "CompanyProfile",
    "AccountStatus",
    "MemberSummary",
    "ContributionSubmission",
    "ContributionStatistics",
    "ComplianceStatus",
    "LegalCase",
    "MemberReference",
    "Employer",
    "EmployerResponse",
    "EmployerSearchResponse",
    # Search
    "SearchRequest",
    "VectorSearchRequest",
    "SearchFilters",
    "PaginationInfo",
    "FacetBucket",
    "Facet",
    "SearchResponse",
    # Dashboard
    "DashboardStats",
    "MemberDashboardStats",
    "EmployerDashboardStats"
]
