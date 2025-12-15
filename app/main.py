"""
Flowist - Context-Aware Meditation Agent

Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.admin.router import router as admin_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Flowist API",
    description="Context-aware meditation agent API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501", 
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/admin")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "flowist"}
