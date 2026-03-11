"""
IP-based Block List Middleware
──────────────────────────────
Supports two blocking mechanisms:
  1. A hardcoded permanent block set (for known bad actors).
  2. A dynamic cache-based block list (e.g. set by throttling logic).

To dynamically block an IP for 24 hours from anywhere in your code:
    from django.core.cache import cache
    cache.set(f"blocked_ip:{ip}", True, timeout=86400)
"""

import logging

from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger("middleware.ip_filter")

# Add known malicious IPs here as strings, e.g. {"1.2.3.4", "5.6.7.8"}
PERMANENTLY_BLOCKED_IPS: set[str] = set()


class IPFilterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self._get_ip(request)

        # Check permanent block list
        if ip in PERMANENTLY_BLOCKED_IPS:
            return JsonResponse({"error": "Forbidden"}, status=403)

        # Check dynamic block list (cache-based, set by throttling logic)
        if cache.get(f"blocked_ip:{ip}"):
            logger.warning("Blocked IP attempted access: %s", ip)
            return JsonResponse({"error": "Too many requests"}, status=429)

        return self.get_response(request)

    @staticmethod
    def _get_ip(request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
