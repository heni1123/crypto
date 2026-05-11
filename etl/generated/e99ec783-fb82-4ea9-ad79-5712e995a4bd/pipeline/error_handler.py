import asyncio
import logging
import time
from typing import Callable, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def retry_with_backoff(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Optional[Any]:
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                wait_time = self.backoff_factor * (2 ** attempt)
                logger.error(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.2f} seconds.")
                await asyncio.sleep(wait_time)
        logger.critical(f"All {self.max_retries} attempts failed for function {func.__name__}.")
        return None

    async def log_audit(self, run_ts: str, rows_loaded: int, status: str) -> None:
        logger.info(f"Audit Log - Run Timestamp: {run_ts}, Rows Loaded: {rows_loaded}, Status: {status}")

error_handler = ErrorHandler()