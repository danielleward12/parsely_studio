from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from herbarium_processor.config import TMP_DIR

from .routers import batches

app = FastAPI(title="Herbarium Processor Web")

STATIC_DIR = Path(__file__).parent / "static"
FRONTEND_DIST = STATIC_DIR / "frontend" / "dist"
ASSETS_DIR = FRONTEND_DIST / "assets"

# API first
app.include_router(batches.router, prefix="/api")

TMP_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/tmp", StaticFiles(directory=TMP_DIR), name="tmp")


# Health
@app.get("/healthz")
async def healthz():
    return {"ok": True}


# www -> apex
@app.middleware("http")
async def redirect_www_to_apex(request: Request, call_next):
    host = request.headers.get("host", "")
    if host.startswith("www."):
        url = request.url.replace(netloc=host[4:])
        return RedirectResponse(str(url), status_code=301)
    return await call_next(request)


# Serve built assets directly (hashed files)
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# Catch-all SPA fallback (must be last)
if FRONTEND_DIST.exists():
    INDEX_HTML = FRONTEND_DIST / "index.html"

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_catch_all(full_path: str = ""):
        # Don’t hijack API/tmp paths
        if full_path.startswith(("api/", "tmp/")):
            return PlainTextResponse("Not Found", status_code=404)
        # Always revalidate the app shell so a new deployment is picked up on
        # the next navigation; Vite's fingerprinted assets remain cache-safe.
        return FileResponse(
            INDEX_HTML,
            headers={"Cache-Control": "no-cache, must-revalidate"},
        )

else:

    @app.get("/", include_in_schema=False)
    async def no_frontend():
        return PlainTextResponse(
            f"Frontend build not found at {FRONTEND_DIST}. Run `npm run build` and copy dist/ there.",
            status_code=503,
        )
