"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import health, deputes, search, dashboard, scrutins, groupes

app = FastAPI(
    title="DemocratIA API",
    description="API pour le tableau de bord citoyen de l'Assemblee Nationale",
    version="0.1.0",
)

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


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
