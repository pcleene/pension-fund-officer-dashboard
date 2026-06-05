"""
Employer service layer - Business logic for employer operations.
"""
from typing import Optional, Dict, List, Any
import logging

from app.config import settings
from app.search.query_builder import (
    build_employers_compound_operator,
    EMPLOYERS_FACETS,
    EMPLOYERS_FACET_MAPPING
)
from app.search.pagination import (
    search_with_pagination,
    get_employers_projection
)
from app.search.vector_search import vector_search_employers

logger = logging.getLogger(__name__)


class EmployerService:
    """Service for employer-related operations."""

    def __init__(self, db):
        self.db = db
        self.employers = db.employers

    async def search_employers(
        self,
        search_text: Optional[str],
        filters: Dict[str, Any],
        limit: int,
        cursor: Optional[str],
        direction: str,
        use_facets: bool
    ) -> Dict[str, Any]:
        """
        Search employers using Atlas Search with faceting and pagination.

        Args:
            search_text: Optional text to search for
            filters: Dict of filters (account_status, sector, etc.)
            limit: Number of results per page
            cursor: Pagination cursor
            direction: "next" or "prev"
            use_facets: Whether to include facets in response

        Returns:
            Dict with results, pagination, and optional facets
        """
        # Build compound operator
        compound_operator = build_employers_compound_operator(
            search_text=search_text,
            filters=filters
        )

        # Determine facets
        facets_definition = EMPLOYERS_FACETS if use_facets else None

        # Execute search with pagination
        result = await search_with_pagination(
            collection=self.employers,
            index_name=settings.employers_search_index,
            compound_operator=compound_operator,
            facets_definition=facets_definition,
            facet_mapping=EMPLOYERS_FACET_MAPPING if use_facets else None,
            limit=limit,
            cursor=cursor,
            direction=direction,
            projection=get_employers_projection()
        )

        return result

    async def vector_search_employers(
        self,
        query: str,
        filters: Dict[str, Any],
        limit: int,
        num_candidates: int
    ) -> Dict[str, Any]:
        """
        Perform semantic search for employers.

        Args:
            query: Natural language query
            filters: Optional metadata filters
            limit: Number of results
            num_candidates: Number of candidates for vector search

        Returns:
            Dict with results and pagination
        """
        result = await vector_search_employers(
            collection=self.employers,
            query=query,
            filters=filters,
            limit=limit,
            num_candidates=num_candidates
        )

        return result

    async def get_employer_by_id(self, employer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single employer by employer ID.

        Args:
            employer_id: PensionFund employer ID

        Returns:
            Employer document or None if not found
        """
        employer = await self.employers.find_one({"employerId": employer_id})
        return employer

    async def get_employer_submissions(
        self,
        employer_id: str,
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """
        Get paginated submission history for an employer.

        Args:
            employer_id: PensionFund employer ID
            limit: Number of submissions to return
            offset: Number of submissions to skip

        Returns:
            List of submission records
        """
        # Get employer document
        employer = await self.employers.find_one(
            {"employerId": employer_id},
            {"recentSubmissions": 1}
        )

        if not employer:
            return []

        # Extract and paginate submissions
        submissions = employer.get("recentSubmissions", [])

        # Apply pagination
        paginated = submissions[offset:offset + limit]

        return paginated

    async def get_employer_members(
        self,
        employer_id: str,
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """
        Get paginated member list for an employer.

        Args:
            employer_id: PensionFund employer ID
            limit: Number of members to return
            offset: Number of members to skip

        Returns:
            List of member reference records
        """
        # Get employer document
        employer = await self.employers.find_one(
            {"employerId": employer_id},
            {"memberList": 1}
        )

        if not employer:
            return []

        # Extract and paginate member list
        members = employer.get("memberList", [])

        # Apply pagination
        paginated = members[offset:offset + limit]

        return paginated

    async def get_employer_compliance(self, employer_id: str) -> Dict[str, Any]:
        """
        Get compliance status for an employer.

        Args:
            employer_id: PensionFund employer ID

        Returns:
            Dict with compliance status and legal cases
        """
        # Get employer document
        employer = await self.employers.find_one(
            {"employerId": employer_id},
            {
                "complianceStatus": 1,
                "legalCases": 1
            }
        )

        if not employer:
            return {}

        return {
            "complianceStatus": employer.get("complianceStatus", {}),
            "legalCases": employer.get("legalCases", [])
        }

    async def get_employer_statistics(self, employer_id: str) -> Dict[str, Any]:
        """
        Get aggregated statistics for an employer.

        Args:
            employer_id: PensionFund employer ID

        Returns:
            Dict with employer statistics
        """
        employer = await self.employers.find_one(
            {"employerId": employer_id},
            {
                "memberSummary": 1,
                "contributionStats": 1,
                "complianceStatus": 1
            }
        )

        if not employer:
            return {}

        return {
            "memberSummary": employer.get("memberSummary", {}),
            "contributionStats": employer.get("contributionStats", {}),
            "complianceStatus": employer.get("complianceStatus", {})
        }

    async def calculate_compliance_score(
        self,
        compliance_status: Dict[str, Any]
    ) -> float:
        """
        Calculate a compliance score for an employer (0-100).

        Args:
            compliance_status: Compliance status dict

        Returns:
            Compliance score (0-100, higher is better)
        """
        score = 100.0

        # Deduct for arrears
        if compliance_status.get("hasArrears"):
            arrears_amount = compliance_status.get("arrearsAmount", 0)
            # Deduct up to 30 points based on arrears amount
            deduction = min(30, arrears_amount / 10000)
            score -= deduction

        # Deduct for legal cases
        if compliance_status.get("hasLegalCases"):
            num_cases = len(compliance_status.get("activeCases", []))
            # Deduct 15 points per active case (max 45)
            score -= min(45, num_cases * 15)

        # Factor in on-time rate from contribution stats
        # This would need to be passed separately or fetched
        # For now, just return the calculated score

        return max(0.0, score)
