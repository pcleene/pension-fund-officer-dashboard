"""
Member service layer - Business logic for member operations.
"""
from typing import Optional, Dict, List, Any
import logging

from app.config import settings
from app.search.query_builder import (
    build_members_compound_operator,
    MEMBERS_FACETS,
    MEMBERS_FACET_MAPPING
)
from app.search.pagination import (
    search_with_pagination,
    get_members_projection
)
from app.search.vector_search import vector_search_members

logger = logging.getLogger(__name__)


class MemberService:
    """Service for member-related operations."""

    def __init__(self, db):
        self.db = db
        self.members = db.members

    async def search_members(
        self,
        search_text: Optional[str],
        filters: Dict[str, Any],
        limit: int,
        cursor: Optional[str],
        direction: str,
        use_facets: bool
    ) -> Dict[str, Any]:
        """
        Search members using Atlas Search with faceting and pagination.

        Args:
            search_text: Optional text to search for
            filters: Dict of filters (account_status, region, etc.)
            limit: Number of results per page
            cursor: Pagination cursor
            direction: "next" or "prev"
            use_facets: Whether to include facets in response

        Returns:
            Dict with results, pagination, and optional facets
        """
        # Build compound operator
        compound_operator = build_members_compound_operator(
            search_text=search_text,
            filters=filters
        )

        # Determine facets
        facets_definition = MEMBERS_FACETS if use_facets else None

        # Execute search with pagination
        result = await search_with_pagination(
            collection=self.members,
            index_name=settings.members_search_index,
            compound_operator=compound_operator,
            facets_definition=facets_definition,
            facet_mapping=MEMBERS_FACET_MAPPING if use_facets else None,
            limit=limit,
            cursor=cursor,
            direction=direction,
            projection=get_members_projection()
        )

        return result

    async def vector_search_members(
        self,
        query: str,
        filters: Dict[str, Any],
        limit: int,
        num_candidates: int
    ) -> Dict[str, Any]:
        """
        Perform semantic search using vector embeddings.

        Args:
            query: Natural language query
            filters: Optional metadata filters
            limit: Number of results
            num_candidates: Number of candidates for vector search

        Returns:
            Dict with results and pagination
        """
        result = await vector_search_members(
            collection=self.members,
            query=query,
            filters=filters,
            limit=limit,
            num_candidates=num_candidates
        )

        return result

    async def get_member_by_id(self, member_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single member by member ID.

        Args:
            member_id: PensionFund member ID

        Returns:
            Member document or None if not found
        """
        member = await self.members.find_one({"memberId": member_id})
        return member

    async def get_member_contributions(
        self,
        member_id: str,
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """
        Get paginated contribution history for a member.

        Args:
            member_id: PensionFund member ID
            limit: Number of contributions to return
            offset: Number of contributions to skip

        Returns:
            List of contribution records
        """
        # Get member document
        member = await self.members.find_one(
            {"memberId": member_id},
            {"recentContributions": 1}
        )

        if not member:
            return []

        # Extract and paginate contributions
        contributions = member.get("recentContributions", [])

        # Apply pagination
        paginated = contributions[offset:offset + limit]

        return paginated

    async def get_member_employers(self, member_id: str) -> List[Dict[str, Any]]:
        """
        Get employer history for a member.

        Args:
            member_id: PensionFund member ID

        Returns:
            List of employer history records
        """
        # Get member document
        member = await self.members.find_one(
            {"memberId": member_id},
            {"employerHistory": 1}
        )

        if not member:
            return []

        return member.get("employerHistory", [])

    async def get_member_withdrawals(self, member_id: str) -> List[Dict[str, Any]]:
        """
        Get withdrawal history for a member.

        Args:
            member_id: PensionFund member ID

        Returns:
            List of withdrawal records
        """
        # Get member document
        member = await self.members.find_one(
            {"memberId": member_id},
            {"withdrawalHistory": 1}
        )

        if not member:
            return []

        return member.get("withdrawalHistory", [])

    async def get_member_statistics(self, member_id: str) -> Dict[str, Any]:
        """
        Get aggregated statistics for a member.

        Args:
            member_id: PensionFund member ID

        Returns:
            Dict with member statistics
        """
        member = await self.members.find_one(
            {"memberId": member_id},
            {
                "contributionStats": 1,
                "accountInfo": 1,
                "complianceFlags": 1,
                "eligibilityFlags": 1
            }
        )

        if not member:
            return {}

        return {
            "contributionStats": member.get("contributionStats", {}),
            "accountInfo": member.get("accountInfo", {}),
            "complianceFlags": member.get("complianceFlags", {}),
            "eligibilityFlags": member.get("eligibilityFlags", {})
        }

    async def mask_ic_number(self, ic_number: str) -> str:
        """
        Mask IC number for display (e.g., 900101-**-****).

        Args:
            ic_number: Full IC number

        Returns:
            Masked IC number
        """
        if not ic_number or len(ic_number) < 12:
            return ic_number

        # Format: YYMMDD-SS-NNNN
        # Mask middle and last segments
        parts = ic_number.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-**-****"

        return ic_number
