import json
import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import applications, auth, resume
from app.core.config import get_settings

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("jobpilot.api")
app = FastAPI(title="JobPilot AI API", description="REST API for managing a job search and explainable job matching.", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(resume.router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Report that the API process is running; database readiness is separate."""
    return {"status": "ok", "service": "jobpilot-api"}


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))[:128]
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(json.dumps({"event": "request_failed", "request_id": request_id, "method": request.method, "path": request.url.path}))
        response = JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(json.dumps({"event": "request_completed", "request_id": request_id, "method": request.method, "path": request.url.path, "status_code": response.status_code, "duration_ms": elapsed_ms}))
    return response
