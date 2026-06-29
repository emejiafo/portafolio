"""
FastAPI application entry point
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")
    await async_engine.dispose()


app = FastAPI(
    title="Freelance Management API",
    description="API for managing data science freelance business",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for CV and project assets
uploads_dir = Path(settings.upload_dir).resolve()
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Import and include routers after app is created to avoid circular imports
from app.api.v1.router import api_router
from app.api.public.router import public_router

# Public endpoints
app.include_router(public_router, prefix="/api/public", tags=["Public"])

# API v1 (post-cleanup, no hour-tracker routes)
if settings.enable_admin_api:
    app.include_router(api_router, prefix="/api/v1", tags=["Admin API"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.environment}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Freelance Management API",
        "docs": "/docs",
        "health": "/health"
    }