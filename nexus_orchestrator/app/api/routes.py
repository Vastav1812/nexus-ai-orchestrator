"""
API router configuration.
"""
from fastapi import APIRouter

from app.api.endpoints import agents, crews, tasks, workflows, auth

# Create API router
api_router = APIRouter()

# Include routers from endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(crews.router, prefix="/crews", tags=["Crews"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
