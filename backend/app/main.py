import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
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
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)

    # 2. Preload Transformer Model on startup
    logger.info("Preloading machine learning sequence classification model...")
    service = AIModelInferenceService.get_instance()
    try:
        service.load_model()
    except Exception as e:
        logger.warning(f"Initial model preload encountered: {e}. Model will attempt on-demand load during inference.")

    yield

    # 3. Shutdown cleanup
    logger.info("Application shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-stack AI text detection, authenticity audit, and prompt evaluation platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(analyze.router, prefix=settings.API_V1_STR)
app.include_router(model.router, prefix=settings.API_V1_STR)
app.include_router(history.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": "Detect AI Writing. Analyze Text. Explore Authenticity.",
        "status": "operational",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
    }
