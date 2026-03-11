"""
Security Headers Middleware
───────────────────────────
Adds essential security headers to every HTTP response to protect against
common web vulnerabilities (clickjacking, MIME sniffing, XSS, etc.).
"""


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip strict CSP for Wagtail admin — it uses inline scripts
        # for chooser modals (page, image, snippet pickers).
        # Admin is already protected by authentication.
        is_admin = request.path.startswith('/admin/')

        # Prevent MIME type sniffing
        response["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking (skip for admin — choosers use iframes)
        if not is_admin:
            response["X-Frame-Options"] = "DENY"

        # XSS protection for older browsers
        response["X-XSS-Protection"] = "1; mode=block"

        # Enforce HTTPS — browser will refuse plain HTTP for 1 year
        response["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Content Security Policy (skip for admin)
        if not is_admin:
            # TODO: Update 'connect-src' with your actual frontend domain
            #       when it becomes available. For now allows 'self'.
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self';"
            )

        # Don't leak full referrer to external sites
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Disable browser features the app doesn't need
        response["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response
