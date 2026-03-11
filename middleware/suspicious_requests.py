"""
Suspicious Request Blocker Middleware
─────────────────────────────────────
Inspects the URL path for common attack patterns (path traversal,
SQL injection, XSS, code execution probes, etc.) and blocks matching
requests before they reach any view.
"""

import re
import logging

from django.http import JsonResponse

logger = logging.getLogger("middleware.suspicious_requests")

# Common attack patterns detected in URL paths
SUSPICIOUS_PATTERNS = [
    r"(\.\./|\.\.\\)",                  # Path traversal
    r"(union\s+select|drop\s+table)",   # SQL injection attempts
    r"(<script|javascript:)",           # XSS attempts
    r"(/etc/passwd|/etc/shadow)",       # Linux file probing
    r"(\.php|\.asp|\.jsp)$",            # Wrong extension probing
    r"(\beval\b|\bexec\b)",             # Code execution attempts
]

COMPILED_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_PATTERNS
]


class SuspiciousRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        full_path = request.get_full_path()

        for pattern in COMPILED_PATTERNS:
            if pattern.search(full_path):
                logger.warning(
                    "Suspicious request blocked | "
                    "IP: %s | Path: %s | Pattern: %s",
                    self._get_ip(request),
                    full_path,
                    pattern.pattern,
                )
                return JsonResponse({"error": "Bad request"}, status=400)

        return self.get_response(request)

    @staticmethod
    def _get_ip(request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
