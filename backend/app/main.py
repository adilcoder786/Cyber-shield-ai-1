"""
CyberShield AI — FastAPI backend entrypoint.
"""
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import init_db
from app.routers import url_scan, message_scan, file_scan, history, stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("cybershield")

app = FastAPI(
    title="CyberShield AI",
    description="AI-powered phishing, message, and file risk detection platform — DevHack IIMTU 2026",
    version="1.0.0",
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ---- Security headers on every response ----
@app.middleware("http")
async def security_headers(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Response-Time-ms"] = str(round((time.time() - start) * 1000, 1))
    return response


# ---- Centralized, non-leaky error handling ----
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "detail": exc.errors()},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": "request_error", "detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": "Something went wrong. Please try again."},
    )


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("CyberShield AI backend started in %s mode", settings.APP_ENV)


@app.get("/", tags=["Health"])
def root():
    return {"service": "CyberShield AI", "status": "online", "version": "1.0.0"}


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok"}


app.include_router(url_scan.router)
app.include_router(message_scan.router)
app.include_router(file_scan.router)
app.include_router(history.router)
app.include_router(stats.router)
