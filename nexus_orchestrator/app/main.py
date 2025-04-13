"""
Nexus AI Orchestrator - Main Application
"""
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.db.session import create_tables

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-agent AI orchestration system",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    # Create database tables
    create_tables()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Nexus AI Orchestration API",
        "docs": "/docs",
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
