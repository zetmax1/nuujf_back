"""
Request Size Limiter Middleware
───────────────────────────────
Enforces maximum request body size to prevent oversized payloads from
reaching the application. File-upload endpoints get a higher limit.
"""

from django.http import JsonResponse


# 60 MB for file upload endpoints and admin CMS
MAX_UPLOAD_SIZE = 60 * 1024 * 1024

# 20 MB for all other (non-upload) requests
MAX_BODY_SIZE = 20 * 1024 * 1024

# Endpoints that accept file uploads — add new upload paths here
UPLOAD_PATHS = (
    "/api/common/vacancies/apply/",
    "/api/appeals/submit/",
    "/admin/",  # Wagtail CMS and Django Admin
    "/tinymce/", # TinyMCE file uploads
)


class RequestSizeLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        content_length = request.META.get("CONTENT_LENGTH")

        if content_length:
            try:
                content_length = int(content_length)
            except (ValueError, TypeError):
                return JsonResponse(
                    {"error": "Invalid Content-Length header"}, status=400
                )

            # File upload endpoints get higher limit
            if any(request.path.startswith(p) for p in UPLOAD_PATHS):
                if content_length > MAX_UPLOAD_SIZE:
                    return JsonResponse(
                        {"error": f"File too large. Maximum {MAX_UPLOAD_SIZE // (1024 * 1024)}MB allowed."},
                        status=413,
                    )
            else:
                if content_length > MAX_BODY_SIZE:
                    return JsonResponse(
                        {"error": "Request body too large."},
                        status=413,
                    )

        return self.get_response(request)
