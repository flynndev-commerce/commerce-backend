import functools
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from app.core.config import get_settings
from app.domain.exceptions import ConcurrentModificationException

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_on_conflict(max_retries: int | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    ConcurrentModificationException 발생 시 지정된 횟수만큼 재시도하는 데코레이터입니다.
    낙관적 락 충돌 시 서버 측에서 자동으로 재시도하여 사용자 경험을 향상시킵니다.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal max_retries
            effective_max_retries = max_retries or get_settings().max_retry_count

            last_exception = None
            for attempt in range(effective_max_retries):
                try:
                    return await func(*args, **kwargs)
                except ConcurrentModificationException as e:
                    last_exception = e
                    logger.warning(
                        f"Concurrent modification detected in {func.__name__}. "
                        f"Retrying... (Attempt {attempt + 1}/{effective_max_retries})"
                    )

            # 모든 재시도 실패 시 마지막 예외 전파
            if last_exception:
                logger.error(
                    f"Max retries ({effective_max_retries}) reached for {func.__name__}. "
                    "Raising ConcurrentModificationException."
                )
                raise last_exception
            return None  # Should not be reached

        return wrapper

    return decorator
