import time
from contextlib import contextmanager
from loguru import logger


@contextmanager
def timed_block(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        logger.info("{} took {:.3f}s", name, time.perf_counter() - start)