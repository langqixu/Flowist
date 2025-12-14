"""
Flowist API Router

Main router that aggregates all API version routers.
"""

from fastapi import APIRouter

from app.api.v1 import meditation

api_router = APIRouter()

# Include v1 routes
api_router.include_router(
    meditation.router,
    prefix="/meditation",
    tags=["meditation"],
)
