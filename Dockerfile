# ── Build stage ──────────────────────────────────────────────
FROM python:3.12-slim-bookworm

# Create non-root user
RUN useradd --create-home wagtail

# Port used by this container to serve HTTP
EXPOSE 8086

# Force unbuffered stdout/stderr so logs appear in real-time
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8086

# Install system packages required by Wagtail, Django, PostgreSQL, and Pillow
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    libmagic1 \
 && rm -rf /var/lib/apt/lists/*

# Install project requirements (cached layer — only re-runs when requirements.txt changes)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

# Use /app as the working directory
WORKDIR /app

# Copy project source code
COPY --chown=wagtail:wagtail . .

# Copy and set up entrypoint
COPY --chown=wagtail:wagtail entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create directories that Django/Wagtail may need at runtime
RUN mkdir -p /app/static /app/media /app/logs \
 && chown -R wagtail:wagtail /app

# Switch to non-root user
USER wagtail

ENTRYPOINT ["/entrypoint.sh"]
