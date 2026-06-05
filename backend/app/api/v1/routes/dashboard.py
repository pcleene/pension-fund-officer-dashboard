"""
Dashboard endpoints for PensionFund Officer Dashboard.
Provides aggregated statistics from materialized views.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
import logging

from app.database import get_database
from app.models.dashboard import MemberDashboardStats, EmployerDashboardStats
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_dashboard_service():
    """Dependency to get dashboard service instance."""
    db = await get_database()
    return DashboardService(db)


# ===========================
# MEMBERS DASHBOARD ENDPOINTS
# ===========================

@router.get("/members/stats", response_model=MemberDashboardStats)
async def get_member_dashboard_stats(
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get complete member dashboard statistics from multiple materialized views.

    Combines data from:
    - mv_member_demographics
    - mv_member_balances
    - mv_member_compliance
    - mv_member_contribution_trends (last 12 months)
    """
    try:
        stats = await service.get_member_dashboard_stats()
        return stats

    except Exception as e:
        logger.error(f"Error retrieving member dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")


@router.get("/members/demographics")
async def get_member_demographics(
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get only member demographics data.
    Refreshed every 15-30 minutes.
    """
    try:
        demographics = await service.get_member_demographics()

        if not demographics:
            raise HTTPException(status_code=404, detail="Demographics data not found")

        return demographics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving demographics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve demographics: {str(e)}")


@router.get("/members/balances")
async def get_member_balances(
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get member balance statistics and distributions.
    Refreshed hourly or every 6 hours.
    """
    try:
        balances = await service.get_member_balances()

        if not balances:
            raise HTTPException(status_code=404, detail="Balance data not found")

        return balances

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving balances: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve balances: {str(e)}")


@router.get("/members/contribution-trends")
async def get_member_contribution_trends(
    months: int = Query(12, ge=1, le=24, description="Number of months to retrieve"),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get member contribution trends for specified number of months.
    Refreshed daily.
    """
    try:
        trends = await service.get_member_contribution_trends(months)
        return trends

    except Exception as e:
        logger.error(f"Error retrieving contribution trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trends: {str(e)}")


@router.get("/members/compliance")
async def get_member_compliance(
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get member compliance and eligibility statistics.
    Refreshed every 30 minutes.
    """
    try:
        compliance = await service.get_member_compliance()

        if not compliance:
            raise HTTPException(status_code=404, detail="Compliance data not found")

        return compliance

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving compliance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compliance: {str(e)}")


# ==============================
# EMPLOYERS DASHBOARD ENDPOINTS
# ==============================

@router.get("/employers/stats", response_model=EmployerDashboardStats)
async def get_employer_dashboard_stats(
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get complete employer dashboard statistics from multiple materialized views.

    Combines data from:
    - mv_employer_profiles
    - mv_employer_compliance
    - mv_employer_workforce
    - mv_employer_submissions (last 12 months)
    """
    try:
        stats = await service.get_employer_dashboard_stats()
        return stats

    except Exception as e:
        logger.error(f"Error retrieving employer dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")


@router.get("/employers/profiles")
async def get_employer_profiles(
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get employer profile and segmentation statistics.
    Refreshed every 6 hours.
    """
    try:
        profiles = await service.get_employer_profiles()

        if not profiles:
            raise HTTPException(status_code=404, detail="Profile data not found")

        return profiles

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profiles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profiles: {str(e)}")


@router.get("/employers/compliance")
async def get_employer_compliance(
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get employer compliance statistics (arrears, legal cases, etc.).
    Refreshed every 3-6 hours.
    """
    try:
        compliance = await service.get_employer_compliance()

        if not compliance:
            raise HTTPException(status_code=404, detail="Compliance data not found")

        return compliance

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving compliance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compliance: {str(e)}")


@router.get("/employers/workforce")
async def get_employer_workforce(
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get employer workforce distribution statistics.
    Refreshed daily.
    """
    try:
        workforce = await service.get_employer_workforce()

        if not workforce:
            raise HTTPException(status_code=404, detail="Workforce data not found")

        return workforce

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving workforce: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve workforce: {str(e)}")


@router.get("/employers/submission-trends")
async def get_employer_submission_trends(
    months: int = Query(12, ge=1, le=24, description="Number of months to retrieve"),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get employer submission trends for specified number of months.
    Refreshed daily.
    """
    try:
        trends = await service.get_employer_submission_trends(months)
        return trends

    except Exception as e:
        logger.error(f"Error retrieving submission trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trends: {str(e)}")


# ====================================
# MATERIALIZED VIEWS REFRESH ENDPOINT
# ====================================

@router.post("/refresh")
async def refresh_materialized_views(
    views: List[str] = Query(["all"], description="Views to refresh"),
    force: bool = Query(False, description="Force refresh bypassing cache"),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Manually refresh materialized views.

    Available views:
    - member_demographics
    - member_balances
    - member_contribution_trends
    - member_compliance
    - employer_profiles
    - employer_compliance
    - employer_workforce
    - employer_submissions
    - all (default - refresh all views)
    """
    try:
        results = await service.refresh_views(views, force)
        return results

    except Exception as e:
        logger.error(f"Error refreshing materialized views: {e}")
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")
