"""
Admin Panel Protection Middleware
─────────────────────────────────
Restricts access to admin panel paths by IP address.
Unauthorized attempts receive a 404 (stealth — attacker won't know
the admin panel exists).

How to activate IP restriction:
  1. Set ADMIN_IP_RESTRICTION_ENABLED = True
  2. Add your office/server IPs to ADMIN_ALLOWED_IPS
  3. Restart the server

Currently disabled — all IPs are allowed through.
"""

import logging

from django.http import Http404

logger = logging.getLogger("middleware.admin_protection")

# ──────────────────────────────────────────────────────────────
# TODO: When ready to lock down admin access, set this to True
#       and add your real office/server IPs to the set below.
# ──────────────────────────────────────────────────────────────
ADMIN_IP_RESTRICTION_ENABLED = False

# Only these IPs will be allowed to access /admin/ and /django-admin/
# when restriction is enabled.
ADMIN_ALLOWED_IPS: set[str] = {
    "127.0.0.1",
    # "YOUR_OFFICE_IP_HERE",
    # "YOUR_SERVER_IP_HERE",
}

# Paths protected by this middleware
PROTECTED_PATHS = ("/admin/", "/django-admin/")


class AdminIPWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip check if restriction is disabled
        if not ADMIN_IP_RESTRICTION_ENABLED:
            return self.get_response(request)

        if request.path.startswith(PROTECTED_PATHS):
            ip = self._get_ip(request)
            if ip not in ADMIN_ALLOWED_IPS:
                logger.warning(
                    "Unauthorized admin access attempt | IP: %s | Path: %s",
                    ip,
                    request.path,
                )
                raise Http404  # stealth — looks like page doesn't exist

        return self.get_response(request)

    @staticmethod
    def _get_ip(request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
