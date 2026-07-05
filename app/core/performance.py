import time
from contextlib import contextmanager
from loguru import logger


@contextmanager
def timed_block(
    name: str,
    *,
    threshold_seconds: float = 0.25,
    always_log: bool = False,
):
    start = time.perf_counter()

    try:
        yield
    finally:
        duration = time.perf_counter() - start

        if always_log or duration >= threshold_seconds:
            logger.info("{} took {:.3f}s", name, duration)