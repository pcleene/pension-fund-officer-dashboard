"""
Dashboard service layer - Business logic for dashboard operations.
Queries materialized views for fast dashboard responses.
"""
from typing import Dict, Any, List
import logging
import time
from datetime import datetime

from app.aggregations import (
    refresh_member_demographics,
    refresh_member_balances,
    refresh_member_contribution_trends,
    refresh_member_compliance,
    refresh_employer_profiles,
    refresh_employer_compliance,
    refresh_employer_workforce,
    refresh_employer_submissions,
    refresh_all_views
)

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard statistics from materialized views."""

    def __init__(self, db):
        self.db = db

    # ===========================
    # MEMBER DASHBOARD METHODS
    # ===========================

    async def get_member_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get complete member dashboard statistics.

        TODO: Query all member materialized views:
        - mv_member_demographics
        - mv_member_balances
        - mv_member_compliance
        - mv_member_contribution_trends (last 12 months)
        """
        demographics = await self.get_member_demographics()
        balances = await self.get_member_balances()
        compliance = await self.get_member_compliance()
        trends = await self.get_member_contribution_trends(12)

        return {
            "demographics": demographics,
            "balances": balances,
            "compliance": compliance,
            "contributionTrends": trends,
            "refreshedAt": demographics.get("refreshedAt") if demographics else None
        }

    async def get_member_demographics(self) -> Dict[str, Any]:
        """Query mv_member_demographics collection."""
        result = await self.db.mv_member_demographics.find_one({"_id": "demographics_summary"})
        return result

    async def get_member_balances(self) -> Dict[str, Any]:
        """Query mv_member_balances collection."""
        result = await self.db.mv_member_balances.find_one({"_id": "balance_summary"})
        return result

    async def get_member_contribution_trends(self, months: int) -> List[Dict[str, Any]]:
        """Query mv_member_contribution_trends collection."""
        cursor = self.db.mv_member_contribution_trends.find({}).sort("month", -1).limit(months)
        results = await cursor.to_list(length=months)
        return results

    async def get_member_compliance(self) -> Dict[str, Any]:
        """Query mv_member_compliance collection."""
        result = await self.db.mv_member_compliance.find_one({"_id": "compliance_summary"})
        return result

    # ==============================
    # EMPLOYER DASHBOARD METHODS
    # ==============================

    async def get_employer_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get complete employer dashboard statistics.

        TODO: Query all employer materialized views:
        - mv_employer_profiles
        - mv_employer_compliance
        - mv_employer_workforce
        - mv_employer_submissions (last 12 months)
        """
        profiles = await self.get_employer_profiles()
        compliance = await self.get_employer_compliance()
        workforce = await self.get_employer_workforce()
        trends = await self.get_employer_submission_trends(12)

        return {
            "profiles": profiles,
            "compliance": compliance,
            "workforce": workforce,
            "submissionTrends": trends,
            "refreshedAt": profiles.get("refreshedAt") if profiles else None
        }

    async def get_employer_profiles(self) -> Dict[str, Any]:
        """Query mv_employer_profiles collection."""
        result = await self.db.mv_employer_profiles.find_one({"_id": "employer_profiles"})
        return result

    async def get_employer_compliance(self) -> Dict[str, Any]:
        """Query mv_employer_compliance collection."""
        result = await self.db.mv_employer_compliance.find_one({"_id": "employer_compliance"})
        return result

    async def get_employer_workforce(self) -> Dict[str, Any]:
        """Query mv_employer_workforce collection."""
        result = await self.db.mv_employer_workforce.find_one({"_id": "workforce_summary"})
        return result

    async def get_employer_submission_trends(self, months: int) -> List[Dict[str, Any]]:
        """Query mv_employer_submissions collection."""
        cursor = self.db.mv_employer_submissions.find({}).sort("month", -1).limit(months)
        results = await cursor.to_list(length=months)
        return results

    # ====================================
    # MATERIALIZED VIEWS REFRESH
    # ====================================

    async def refresh_views(self, views: List[str], force: bool) -> Dict[str, Any]:
        """
        Manually refresh materialized views.

        Args:
            views: List of view names to refresh, or ["all"] for all views
            force: Force refresh bypassing any caching (currently unused)

        Returns:
            Dict with refresh results for each view

        Available views:
        - member_demographics
        - member_balances
        - member_contribution_trends
        - member_compliance
        - employer_profiles
        - employer_compliance
        - employer_workforce
        - employer_submissions
        - all
        """
        results = {}

        # Determine which views to refresh
        if "all" in views:
            logger.info("Refreshing all materialized views...")
            start_time = time.time()

            try:
                await refresh_all_views(self.db)
                duration = time.time() - start_time

                results["all"] = {
                    "status": "success",
                    "duration_seconds": round(duration, 2),
                    "refreshed_at": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error refreshing all views: {e}")
                results["all"] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            # Refresh individual views
            view_functions = {
                "member_demographics": refresh_member_demographics,
                "member_balances": refresh_member_balances,
                "member_contribution_trends": refresh_member_contribution_trends,
                "member_compliance": refresh_member_compliance,
                "employer_profiles": refresh_employer_profiles,
                "employer_compliance": refresh_employer_compliance,
                "employer_workforce": refresh_employer_workforce,
                "employer_submissions": refresh_employer_submissions
            }

            for view in views:
                if view not in view_functions:
                    results[view] = {
                        "status": "error",
                        "error": f"Unknown view: {view}"
                    }
                    continue

                try:
                    start_time = time.time()
                    await view_functions[view](self.db)
                    duration = time.time() - start_time

                    results[view] = {
                        "status": "success",
                        "duration_seconds": round(duration, 2),
                        "refreshed_at": datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"Error refreshing {view}: {e}")
                    results[view] = {
                        "status": "error",
                        "error": str(e)
                    }

        return {
            "refreshed_at": datetime.now().isoformat(),
            "results": results
        }
