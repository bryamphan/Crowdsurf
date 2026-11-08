"""Entry point of the backend. Start reading here.

Creates the FastAPI app, sets up CORS so the frontend can call the API, and registers
every router. All API routes live under /api/v1; the health checks live at /health.

What's left to do:
- Register new routers here as they're added (e.g. an auth router for host signup/login).
- Start background jobs on startup, such as the room expiry job.
"""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import guests, health, playback, queue, rooms, tracks

settings = get_settings()

app = FastAPI(title="Crowdsurf API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api/v1")
for module in (rooms, guests, tracks, queue, playback):
    api.include_router(module.router)

app.include_router(health.router)
app.include_router(api)
