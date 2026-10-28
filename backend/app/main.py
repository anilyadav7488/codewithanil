import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.database.session import engine, Base
import app.models # Ensure models are loaded
from app.api.v1 import auth, analyze, model, history, reports
from ml.inference import AIModelInferenceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("codewithanil")

# Set up rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Create tables
    logger.info("[Startup] Initializing database schemas...")
    Base.metadata.create_all(bind=engine)

    # 2. Preload ML Model on startup
    logger.info("[Startup] Preloading machine learning inference engine...")
    service = AIModelInferenceService.get_instance()
    try:
        success = service.load_model()
        if success:
            logger.info("[Startup] ML model successfully preloaded into memory.")
        else:
            logger.warning(f"[Startup Warning] Model preload did not complete: {getattr(service, 'load_error', 'unknown error')}. Will retry on demand.")
    except Exception as e:
        logger.error(f"[Startup Error] Exception while preloading model: {e}", exc_info=True)

    yield

    # 3. Shutdown cleanup
    logger.info("[Shutdown] Application shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-stack AI text detection, authenticity audit, and prompt evaluation platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS with Vercel regex support for dynamic preview branches
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers under /api
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(analyze.router, prefix=settings.API_V1_STR)
app.include_router(model.router, prefix=settings.API_V1_STR)
app.include_router(history.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)

# Direct fallbacks without /api prefix (prevents 404 if reverse proxy or frontend client strips /api)
app.include_router(analyze.router)
app.include_router(model.router)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": "Detect AI Writing. Analyze Text. Explore Authenticity.",
        "status": "operational",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "ready": f"{settings.API_V1_STR}/ready",
    }
