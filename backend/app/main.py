# DemocratIA - FastAPI application entry point

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

# Rate limiting: 100 requests per minute per IP (added first = runs inner)
app.add_middleware(RateLimitMiddleware)

# CORS: added last = runs outermost, so headers are set even on 500 errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    logger.info("CORS origins: allow all")
    logger.info("DemocratIA API started successfully")
