from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from backend.app.core.config import get_settings
from backend.app.api.routes import workflows, approvals, tenants

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Beauty Growth System", version="0.1.0")
    yield
    logger.info("Shutting down Beauty Growth System")


app = FastAPI(
    title=settings.app_name,
    description="Multi-Agent AI Growth System for Chinese Medical Aesthetics",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(approvals.router, prefix="/api/v1/approvals", tags=["approvals"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Beauty Growth System API",
        "docs": "/docs",
        "health": "/health",
    }
