"""
Main API router that aggregates all v1 endpoints.
"""
from fastapi import APIRouter

from app.api.v1.routes import members, employers, dashboard, search

api_router = APIRouter()

# Include route modules
api_router.include_router(
    members.router,
    prefix="/members",
    tags=["Members"]
)

api_router.include_router(
    employers.router,
    prefix="/employers",
    tags=["Employers"]
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["Search"]
)
