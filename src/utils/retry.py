"""
Utility decorators and functions for retry logic with exponential backoff.

Provides retry decorators for API calls to external services (Notion, Drive, etc.)
to handle transient failures like rate limits, network issues, and temporary outages.
"""

import asyncio
import functools
import logging
from typing import Type, Tuple, Optional, Callable

logger = logging.getLogger(__name__)


def async_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Async retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        backoff_factor: Multiplier for delay after each retry (default: 2.0)
        exceptions: Tuple of exception types to catch and retry (default: all Exceptions)
        on_retry: Optional callback function called on each retry attempt

    Example:
        @async_retry(max_retries=3, exceptions=(ConnectionError, TimeoutError))
        async def api_call():
            # Make API request
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries - 1:
                        # Last attempt failed, log and raise
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts. "
                            f"Final error: {type(e).__name__}: {e}"
                        )
                        raise e

                    # Log retry attempt
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_retries} failed. "
                        f"Error: {type(e).__name__}: {e}. Retrying in {delay:.1f}s..."
                    )

                    # Call on_retry callback if provided
                    if on_retry:
                        try:
                            await on_retry(attempt + 1, e)
                        except Exception as callback_error:
                            logger.error(f"on_retry callback failed: {callback_error}")

                    # Exponential backoff
                    await asyncio.sleep(delay)
                    delay *= backoff_factor

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def sync_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Synchronous retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        backoff_factor: Multiplier for delay after each retry (default: 2.0)
        exceptions: Tuple of exception types to catch and retry (default: all Exceptions)
        on_retry: Optional callback function called on each retry attempt

    Example:
        @sync_retry(max_retries=3, exceptions=(ConnectionError, TimeoutError))
        def api_call():
            # Make API request
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries - 1:
                        # Last attempt failed, log and raise
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts. "
                            f"Final error: {type(e).__name__}: {e}"
                        )
                        raise e

                    # Log retry attempt
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_retries} failed. "
                        f"Error: {type(e).__name__}: {e}. Retrying in {delay:.1f}s..."
                    )

                    # Call on_retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e)
                        except Exception as callback_error:
                            logger.error(f"on_retry callback failed: {callback_error}")

                    # Exponential backoff
                    time.sleep(delay)
                    delay *= backoff_factor

        return wrapper
    return decorator


__all__ = ['async_retry', 'sync_retry']
