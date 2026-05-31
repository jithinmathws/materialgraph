import sys

from loguru import logger
from app.core.config import settings

logger.remove()

logger.add(
    sys.stdout,
    level=settings.log_level,
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level} | "
        "{name}:{function}:{line} | "
        "{message}"
    ),
)

__all__ = ["logger"]