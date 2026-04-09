"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .middleware.rate_limit import RateLimitMiddleware
from .routers import health, deputes, search, dashboard, scrutins, groupes, ia, stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DemocratIA API",
    description="API pour le tableau de bord citoyen de l'Assemblee Nationale",
    version="1.0.0",
)

# CORS: restrict in production, allow all in development
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]
if hasattr(settings, "CORS_ORIGINS") and settings.CORS_ORIGINS:
    ALLOWED_ORIGINS = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Rate limiting: 100 requests per minute per IP
app.add_middleware(RateLimitMiddleware)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(deputes.router, prefix="/api", tags=["deputes"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(scrutins.router, prefix="/api", tags=["scrutins"])
app.include_router(groupes.router, prefix="/api", tags=["groupes"])
app.include_router(ia.router, prefix="/api", tags=["ia"])
app.include_router(stats.router, prefix="/api", tags=["stats"])


@app.on_event("startup")
def on_startup():
    logger.info("Starting DemocratIA API...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready")
    logger.info(f"CORS origins: {ALLOWED_ORIGINS}")
    logger.info("DemocratIA API started successfully")
