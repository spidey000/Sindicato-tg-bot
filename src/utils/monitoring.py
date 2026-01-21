"""
Basic monitoring utilities for tracking API failures and success rates.

Provides simple metrics collection for:
- API success/failure rates
- Latency tracking
- Rate limit detection
- Error categorization
"""

import time
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class APIMetrics:
    """Simple in-memory metrics tracker for API calls."""

    def __init__(self):
        self._calls: Dict[str, list] = defaultdict(list)
        self._errors: Dict[str, list] = defaultdict(list)
        self._rate_limits: Dict[str, int] = defaultdict(int)

    def record_call(self, api_name: str, success: bool, latency_ms: float = None, error_type: str = None):
        """
        Record an API call with its result.

        Args:
            api_name: Name of the API (e.g., 'notion', 'drive', 'perplexity', 'openrouter')
            success: Whether the call succeeded
            latency_ms: Optional latency in milliseconds
            error_type: Optional error type/category for failures
        """
        timestamp = datetime.now()

        if success:
            self._calls[api_name].append({
                'timestamp': timestamp,
                'success': True,
                'latency_ms': latency_ms
            })
            logger.debug(f"✅ {api_name} call succeeded ({latency_ms:.0f}ms)" if latency_ms else f"✅ {api_name} call succeeded")
        else:
            self._calls[api_name].append({
                'timestamp': timestamp,
                'success': False,
                'error_type': error_type
            })
            self._errors[api_name].append({
                'timestamp': timestamp,
                'error_type': error_type
            })
            logger.warning(f"❌ {api_name} call failed ({error_type or 'unknown error'})")

            # Detect rate limit errors
            if error_type and 'rate' in error_type.lower():
                self._rate_limits[api_name] += 1
                logger.error(f"🚨 Rate limit hit for {api_name} (total: {self._rate_limits[api_name]})")

    def get_success_rate(self, api_name: str, minutes: int = 60) -> Optional[float]:
        """
        Calculate success rate for an API in the last N minutes.

        Args:
            api_name: Name of the API
            minutes: Time window in minutes (default: 60)

        Returns:
            Success rate as percentage (0-100), or None if no calls recorded
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_calls = [c for c in self._calls[api_name] if c['timestamp'] >= cutoff]

        if not recent_calls:
            return None

        successful = sum(1 for c in recent_calls if c['success'])
        total = len(recent_calls)

        return (successful / total) * 100 if total > 0 else 0.0

    def get_average_latency(self, api_name: str, minutes: int = 60) -> Optional[float]:
        """
        Calculate average latency for an API in the last N minutes.

        Args:
            api_name: Name of the API
            minutes: Time window in minutes (default: 60)

        Returns:
            Average latency in milliseconds, or None if no successful calls recorded
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_calls = [
            c for c in self._calls[api_name]
            if c['timestamp'] >= cutoff and c['success'] and c.get('latency_ms')
        ]

        if not recent_calls:
            return None

        latencies = [c['latency_ms'] for c in recent_calls]
        return sum(latencies) / len(latencies)

    def get_error_summary(self, api_name: str, minutes: int = 60) -> Dict[str, int]:
        """
        Get error breakdown by type for an API in the last N minutes.

        Args:
            api_name: Name of the API
            minutes: Time window in minutes (default: 60)

        Returns:
            Dictionary mapping error types to counts
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_errors = [e for e in self._errors[api_name] if e['timestamp'] >= cutoff]

        summary = defaultdict(int)
        for error in recent_errors:
            error_type = error['error_type'] or 'unknown'
            summary[error_type] += 1

        return dict(summary)

    def get_all_metrics(self, minutes: int = 60) -> Dict[str, Dict]:
        """
        Get comprehensive metrics for all APIs.

        Args:
            minutes: Time window in minutes (default: 60)

        Returns:
            Dictionary with metrics for each API
        """
        metrics = {}

        for api_name in self._calls.keys():
            metrics[api_name] = {
                'success_rate': self.get_success_rate(api_name, minutes),
                'avg_latency_ms': self.get_average_latency(api_name, minutes),
                'error_summary': self.get_error_summary(api_name, minutes),
                'rate_limit_hits': self._rate_limits.get(api_name, 0)
            }

        return metrics

    def log_summary(self, minutes: int = 60):
        """
        Log a summary of all API metrics.

        Args:
            minutes: Time window in minutes (default: 60)
        """
        metrics = self.get_all_metrics(minutes)

        logger.info("=" * 60)
        logger.info(f"📊 API METRICS SUMMARY (last {minutes} minutes)")
        logger.info("=" * 60)

        for api_name, api_metrics in metrics.items():
            logger.info(f"\n🔹 {api_name.upper()}")
            logger.info(f"  Success Rate: {api_metrics['success_rate']:.1f}%")
            if api_metrics['avg_latency_ms']:
                logger.info(f"  Avg Latency: {api_metrics['avg_latency_ms']:.0f}ms")
            if api_metrics['error_summary']:
                logger.info(f"  Errors: {api_metrics['error_summary']}")
            if api_metrics['rate_limit_hits'] > 0:
                logger.error(f"  ⚠️ Rate Limit Hits: {api_metrics['rate_limit_hits']}")

        logger.info("=" * 60)

    def reset(self):
        """Clear all recorded metrics."""
        self._calls.clear()
        self._errors.clear()
        self._rate_limits.clear()
        logger.info("🔄 Metrics reset")


# Global metrics instance
api_metrics = APIMetrics()


def track_api_call(api_name: str):
    """
    Decorator to automatically track API calls.

    Usage:
        @track_api_call('notion')
        def create_page(...):
            ...

    Args:
        api_name: Name of the API being called
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_type = None

            try:
                result = await func(*args, **kwargs)
                success = result is not None
                return result
            except Exception as e:
                error_type = type(e).__name__
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                api_metrics.record_call(api_name, success, latency_ms, error_type)

        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_type = None

            try:
                result = func(*args, **kwargs)
                success = result is not None
                return result
            except Exception as e:
                error_type = type(e).__name__
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                api_metrics.record_call(api_name, success, latency_ms, error_type)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


__all__ = ['APIMetrics', 'api_metrics', 'track_api_call']
