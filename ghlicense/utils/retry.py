"""Retry utilities with exponential backoff for API rate limiting."""
import asyncio
import functools
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Exception raised when API rate limit is exceeded."""

    def __init__(self, message: str, response: Optional[Any] = None):
        super().__init__(message)
        self.response = response


def async_retry(max_retries: int = 5, base_delay: float = 1.0):
    """Decorator that retries async functions with exponential backoff.

    Handles HTTP 429 (Too Many Requests) and other rate limit errors.
    Exponential backoff: 1s, 2s, 4s, 8s, 16s for max_retries=5.
    Respects Retry-After header if present in the response.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except RateLimitError as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                        raise

                    delay = _calculate_delay(e, attempt, base_delay)
                    logger.warning(f"Rate limit hit for {func.__name__}, retry {attempt + 1}/{max_retries - 1} in {delay:.1f}s")
                    await asyncio.sleep(delay)
                except Exception as e:
                    if _is_rate_limit_error(e):
                        last_exception = RateLimitError(str(e))
                        if attempt == max_retries - 1:
                            logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                            raise last_exception

                        delay = _calculate_delay(last_exception, attempt, base_delay)
                        logger.warning(f"Rate limit error for {func.__name__}, retry {attempt + 1}/{max_retries - 1} in {delay:.1f}s")
                        await asyncio.sleep(delay)
                    else:
                        raise

            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def _calculate_delay(exception: RateLimitError, attempt: int, base_delay: float) -> float:
    """Calculate delay for exponential backoff."""
    response = getattr(exception, 'response', None)
    if response and hasattr(response, 'headers'):
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return float(retry_after)
            except (ValueError, TypeError):
                pass

    return base_delay * (2 ** attempt)


def _is_rate_limit_error(exception: Exception) -> bool:
    """Check if exception is rate limit related."""
    error_msg = str(exception).lower()
    rate_limit_indicators = ['429', 'too many requests', 'rate limit', 'rate limit exceeded']

    if hasattr(exception, 'response'):
        response = exception.response
        if hasattr(response, 'status') and response.status == 429:
            return True

    return any(indicator in error_msg for indicator in rate_limit_indicators)