from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MaterialGraph starting up")
    logger.info("Environment: {}", settings.environment)

    yield

    logger.info("MaterialGraph shutting down")


app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="Graph-based material intelligence platform",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.project_name,
        "environment": settings.environment,
    }