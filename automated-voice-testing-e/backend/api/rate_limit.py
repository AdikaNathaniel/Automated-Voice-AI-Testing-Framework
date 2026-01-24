"""
Request rate limiting utilities.

Provides per-identifier (user/IP) throttling using Redis as backing store.
Supports per-endpoint rate limits and trusted proxy validation.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import time
from typing import Optional

from fastapi import Request

from api.redis_client import get_redis
from api.config import get_settings

KEY_PREFIX = "rate-limit"
DETAIL_MESSAGE = "Rate limit exceeded. Try again later."


def _get_rate_limit_config(path: str) -> tuple[int, int]:
    """
    Get rate limit configuration for a given path.

    Args:
        path: Request path

    Returns:
        tuple: (requests_per_window, window_seconds)
    """
    settings = get_settings()

    # Stricter limits for auth endpoints
    if path.startswith("/api/v1/auth/"):
        return (
            settings.RATE_LIMIT_AUTH_REQUESTS,
            settings.RATE_LIMIT_AUTH_WINDOW
        )

    # Default limits for all other endpoints
    return (
        settings.RATE_LIMIT_DEFAULT_REQUESTS,
        settings.RATE_LIMIT_DEFAULT_WINDOW
    )


def _is_trusted_proxy(ip: str) -> bool:
    """
    Check if an IP is a trusted proxy.

    Args:
        ip: IP address to check

    Returns:
        bool: True if IP is trusted
    """
    settings = get_settings()
    trusted = settings.RATE_LIMIT_TRUSTED_PROXIES.split(",")

    try:
        client_ip = ipaddress.ip_address(ip.strip())

        for trusted_ip in trusted:
            trusted_ip = trusted_ip.strip()
            if "/" in trusted_ip:
                # CIDR notation
                if client_ip in ipaddress.ip_network(trusted_ip, strict=False):
                    return True
            else:
                # Single IP
                if client_ip == ipaddress.ip_address(trusted_ip):
                    return True
    except ValueError:
        pass

    return False


class RateLimitExceeded(Exception):
    """Raised when a client exceeds the configured rate limit."""

    def __init__(self, retry_after: int) -> None:
        super().__init__(DETAIL_MESSAGE)
        self.retry_after = max(retry_after, 0)


async def enforce_rate_limit(request: Request) -> None:
    """
    Enforce per-user (or per-client) rate limiting.

    Supports per-endpoint rate limits with stricter limits for auth endpoints.

    Args:
        request: Incoming FastAPI request.

    Raises:
        RateLimitExceeded: When the identifier has exceeded the quota.
    """
    # Get endpoint-specific rate limit configuration
    rate_limit_requests, window_seconds = _get_rate_limit_config(request.url.path)

    identifier = _resolve_identifier(request)
    if identifier is None:
        # No identifier means we cannot reliably enforce rate limits.
        return

    # Include path prefix in key for per-endpoint limits
    path_prefix = "auth" if request.url.path.startswith("/api/v1/auth/") else "default"
    cache_key = f"{KEY_PREFIX}:{path_prefix}:{identifier}"

    now = int(time.time())
    redis_gen = get_redis()
    redis = await redis_gen.__anext__()

    try:
        existing = await redis.get(cache_key)
        if existing is None:
            payload = {"count": 1, "reset": now + window_seconds}
            await redis.set(cache_key, json.dumps(payload), ttl=window_seconds)
            return

        try:
            data = json.loads(existing)
        except json.JSONDecodeError:
            data = {"count": 0, "reset": now}

        count = int(data.get("count", 0))
        reset_ts = int(data.get("reset", now + window_seconds))

        if now >= reset_ts:
            new_payload = {"count": 1, "reset": now + window_seconds}
            await redis.set(cache_key, json.dumps(new_payload), ttl=window_seconds)
            return

        if count >= rate_limit_requests:
            raise RateLimitExceeded(retry_after=reset_ts - now)

        count += 1
        remaining_window = max(1, reset_ts - now)
        updated_payload = {"count": count, "reset": reset_ts}
        await redis.set(cache_key, json.dumps(updated_payload), ttl=remaining_window)
    finally:
        try:
            await redis_gen.aclose()
        except StopAsyncIteration:  # pragma: no cover - defensive cleanup
            pass


def _resolve_identifier(request: Request) -> Optional[str]:
    """
    Derive a stable identifier for the caller.

    Preference order:
        1. Authorization header contents (hashed)
        2. Real client IP (from X-Forwarded-For if behind trusted proxy)

    Validates X-Forwarded-For headers to prevent spoofing.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header:
        token = auth_header.split(" ", 1)[-1].strip()
        if token:
            return _hash_identifier(f"user:{token}")

    # Get client IP, respecting X-Forwarded-For only from trusted proxies
    client_ip = _get_client_ip(request)
    if client_ip:
        return _hash_identifier(f"ip:{client_ip}")

    return None


def _get_client_ip(request: Request) -> Optional[str]:
    """
    Get the real client IP address.

    Validates X-Forwarded-For headers only if the direct connection
    is from a trusted proxy. This prevents IP spoofing attacks.

    Args:
        request: FastAPI request

    Returns:
        str: Client IP address or None
    """
    # Get direct connection IP
    client = request.client
    if not client or not client.host:
        return None

    direct_ip = client.host

    # Check if request is from trusted proxy
    if not _is_trusted_proxy(direct_ip):
        # Not from trusted proxy, use direct IP
        return direct_ip

    # Request is from trusted proxy, check X-Forwarded-For
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # X-Forwarded-For is comma-separated list: client, proxy1, proxy2, ...
        # The leftmost IP is the original client
        ips = [ip.strip() for ip in x_forwarded_for.split(",")]

        # Find the first non-trusted IP from the left
        for ip in ips:
            if ip and not _is_trusted_proxy(ip):
                return ip

        # All IPs are trusted (edge case), use the first one
        if ips and ips[0]:
            return ips[0]

    # Fall back to X-Real-IP header
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip.strip()

    # Fall back to direct IP
    return direct_ip


def _hash_identifier(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return digest
