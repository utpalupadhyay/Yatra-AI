"""
Yatra AI - FastAPI Application Entry Point
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from app.core.config import get_settings
from app.api.routes.trip import router as trip_router

# ── Logging ──────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# ── FastAPI App ───────────────────────────────
app = FastAPI(
    title="Yatra AI",
    description="AI-powered travel planner using Gemma 4 — Plan smarter. Travel better.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static / Frontend Files ───────────────────
BASE_DIR = Path(__file__).resolve().parent
candidates = [
    BASE_DIR / "frontend",
    BASE_DIR / "static",
    BASE_DIR.parent / "frontend",
]
frontend_dir = None
for c in candidates:
    if (c / "index.html").exists():
        frontend_dir = c
        break

if frontend_dir and (frontend_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

# ── Routes ───────────────────────────────────
app.include_router(trip_router)


@app.get("/")
async def root():
    if frontend_dir and (frontend_dir / "index.html").exists():
        return FileResponse(str(frontend_dir / "index.html"))
    return {
        "app": "Yatra AI",
        "tagline": "Plan smarter. Travel better.",
        "powered_by": "Gemma 4 (gemma-4-31b-it)",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/api/info")
async def api_info():
    return {
        "app": "Yatra AI",
        "tagline": "Plan smarter. Travel better.",
        "powered_by": "Gemma 4 (gemma-4-31b-it)",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/favicon.ico")
async def favicon():
    if frontend_dir:
        fav = frontend_dir / "assets" / "images" / "favicon.svg"
        if fav.exists():
            return FileResponse(str(fav), media_type="image/svg+xml")
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "An unexpected error occurred. Please try again."},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
