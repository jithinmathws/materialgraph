from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(title=settings.project_name)

app.include_router(api_router, prefix="/api/v1")