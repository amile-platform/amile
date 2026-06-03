"""
AMILE — Adaptive Mathematics Intelligence & Learning Ecosystem
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.db.session import engine, Base
from app.api.routes import (
    auth, students, teachers, admins,
    assessments, knowledge_tracing,
    analytics, ai_tutor, interventions
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AMILE platform starting up", env=settings.APP_ENV)
    yield
    logger.info("AMILE platform shutting down")


app = FastAPI(
    title="AMILE API",
    description="Adaptive Mathematics Intelligence & Learning Ecosystem",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(auth.router,              prefix="/api/v1/auth",        tags=["Authentication"])
app.include_router(students.router,          prefix="/api/v1/students",    tags=["Students"])
app.include_router(teachers.router,          prefix="/api/v1/teachers",    tags=["Teachers"])
app.include_router(admins.router,            prefix="/api/v1/admins",      tags=["Admins"])
app.include_router(assessments.router,       prefix="/api/v1/assessments", tags=["Assessments"])
app.include_router(knowledge_tracing.router, prefix="/api/v1/kt",          tags=["Knowledge Tracing"])
app.include_router(analytics.router,         prefix="/api/v1/analytics",   tags=["Analytics"])
app.include_router(ai_tutor.router,          prefix="/api/v1/tutor",       tags=["AI Tutor"])
app.include_router(interventions.router,     prefix="/api/v1/interventions",tags=["Interventions"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "platform": "AMILE", "version": "1.0.0"}
