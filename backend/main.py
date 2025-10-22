"""
Green School Management System - Main Application
FastAPI Backend API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from config.database import engine, Base
from config.settings import settings

# Import controllers
from controllers import user_router, school_router, teacher_router, student_router, parent_router, subject_router, room_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the application"""
    # Startup
    logger.info("Starting Green School Management System API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created successfully")

    yield

    # Shutdown
    logger.info("Shutting down Green School Management System API")
    await engine.dispose()


# Initialize FastAPI app
app = FastAPI(
    title="Green School Management System API",
    description="Comprehensive digital platform for primary school administration (Grades 1-7)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Green School Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Include routers
app.include_router(user_router, prefix=settings.API_V1_PREFIX)
app.include_router(school_router, prefix=settings.API_V1_PREFIX)
app.include_router(teacher_router, prefix=settings.API_V1_PREFIX)
app.include_router(student_router, prefix=settings.API_V1_PREFIX)
app.include_router(parent_router, prefix=settings.API_V1_PREFIX)
app.include_router(subject_router, prefix=settings.API_V1_PREFIX)
app.include_router(room_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
