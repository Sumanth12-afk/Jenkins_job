from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry_call(
    operation: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay_seconds: float = 0.5,
    logger: logging.Logger | None = None,
    retry_exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> T:
    last_error: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except retry_exceptions as exc:
            last_error = exc
            if attempt == attempts:
                break
            delay = base_delay_seconds * (2 ** (attempt - 1))
            if logger:
                logger.warning("Retryable operation failed", extra={"attempt": attempt, "delay": delay})
            time.sleep(delay)
    assert last_error is not None
    raise last_error
