# Production Deployment Guide — nuujf

> **What this is:** A step-by-step runbook for deploying the nuujf university platform (Django/Wagtail backend + React/Vite frontend) to a Linux server. Written in the order a real engineer would follow on a fresh machine where Docker is already installed.

> **What this is NOT:** A tutorial. If a step says "do X", do X. If something goes wrong, check §12 Troubleshooting before improvising.

---

## Placeholders — replace these everywhere

| Placeholder          | What to put there                          | Example                      |
|----------------------|--------------------------------------------|------------------------------|
| `YOUR_SERVER_IP`     | Public IPv4 of your server                 | `164.92.xxx.xxx`             |
| `YOUR_DOMAIN`        | Main domain for the frontend               | `nuujf.uz`                   |
| `YOUR_API_DOMAIN`    | Subdomain for the backend API              | `api.nuujf.uz`               |
| `YOUR_EMAIL`         | Email for SSL certificate registration     | `admin@nuujf.uz`             |
| `YOUR_GITHUB_USER`   | GitHub username that owns the repos        | `zetmax1`                    |
| `YOUR_DEPLOY_USER`   | Linux user that runs Docker on the server  | `deploy`                     |

---

## 1. Set up SSH access to GitHub from the server

**Why:** The server needs to pull your private repositories. SSH keys are more secure than embedding passwords in git URLs and don't expire like personal access tokens.

Generate a deploy key on the server:

```bash
ssh-keygen -t ed25519 -C "deploy@YOUR_SERVER_IP" -f ~/.ssh/github_deploy -N ""
```

Print the public key:

```bash
cat ~/.ssh/github_deploy.pub
```

Go to each GitHub repository → **Settings → Deploy keys → Add deploy key**, paste the public key. Check "Allow write access" only if CI/CD needs to push (it doesn't in our setup).

Configure SSH to use this key for GitHub:

```bash
cat >> ~/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_deploy
    IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config
```

Verify it works:

```bash
ssh -T git@github.com
# Expected: "Hi YOUR_GITHUB_USER! You've been authenticated..."
```

---

## 2. Clone both repositories

**Why:** We keep both repos under `/opt/nuujf` so all deployment scripts, compose files, and paths are predictable. The backend repo contains the `docker-compose.prod.yml` that orchestrates everything.

```bash
sudo mkdir -p /opt/nuujf
sudo chown -R $USER:$USER /opt/nuujf
cd /opt/nuujf
```

Clone backend:

```bash
git clone git@github.com:YOUR_GITHUB_USER/nuujf_back.git backend
```

Clone frontend:

```bash
git clone git@github.com:YOUR_GITHUB_USER/jbnuu_front.git frontend
```

Your directory tree should now look like:

```
/opt/nuujf/
├── backend/          ← Django/Wagtail + docker-compose.prod.yml
│   ├── .env          ← you'll create this in §3
│   ├── docker-compose.prod.yml
│   ├── nginx/nuujf.uz.conf
│   └── logs/
└── frontend/         ← React/Vite SPA
    ├── Dockerfile
    └── nginx.conf
```

---

## 3. Create the production `.env` file

**Why:** Every secret and environment-specific value lives in `.env`, which is read by both `docker-compose.prod.yml` and Django's `python-decouple`. This file is in `.gitignore` — it must never be committed.

```bash
cd /opt/nuujf/backend
cp .env.production.example .env
```

Now edit it and replace every `CHANGE_ME` value:

```bash
nano .env
```

Generate the values you need:

```bash
# Generate SECRET_KEY (Django cryptographic signing):
python3 -c "import secrets; print(secrets.token_hex(50))"

# Generate DB_PASSWORD:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate REDIS_PASSWORD:
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

Here's what the final `.env` should look like (with real values filled in):

```env
# ── Django Core ───────────────────────────────────────────────
SECRET_KEY=<output of token_hex(50)>
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=YOUR_API_DOMAIN,YOUR_DOMAIN

# ── Security ─────────────────────────────────────────────────
# Leave SECURE_SSL_REDIRECT=False until §6 confirms SSL works.
# Turning it on before SSL is ready locks you out.
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False

# ── PostgreSQL ────────────────────────────────────────────────
DB_NAME=nuujf_db
DB_USER=nuujf_user
DB_PASSWORD=<output of token_urlsafe(32)>
DB_HOST=db
DB_PORT=5432

# ── Redis ─────────────────────────────────────────────────────
REDIS_PASSWORD=<output of token_urlsafe(24)>
REDIS_URL=redis://:<same password as above>@redis:6379/1

# ── External integrations ────────────────────────────────────
HEMIS_TOKEN=<your real HEMIS API token>

# ── Docker registry ──────────────────────────────────────────
REGISTRY=ghcr.io
IMAGE_TAG=latest
```

**Critical detail about REDIS_URL:** The password appears twice — once in `REDIS_PASSWORD` (used by the Redis container's `--requirepass` flag) and once embedded in `REDIS_URL` (used by Django's cache backend). They must be identical.

---

## 4. Prepare host directories for static and media files

**Why:** The host Nginx (§6) serves static files and uploaded media directly from disk, bypassing Gunicorn entirely. This is 10-50x faster than proxying them through Python. The `docker-compose.prod.yml` bind-mounts these directories into the web container so Django's `collectstatic` and media uploads write to the host filesystem.

```bash
sudo mkdir -p /var/www/nuujf/static
sudo mkdir -p /var/www/nuujf/media
sudo chown -R $USER:$USER /var/www/nuujf
```

Also prepare the logs directory:

```bash
mkdir -p /opt/nuujf/backend/logs
```

---

## 5. Build and start all Docker services

**Why for the first deploy:** We build images locally because CI/CD hasn't pushed any images to the registry yet. After this initial deploy, CI/CD will push pre-built images and the server will only `docker pull`.

### 5a. Build the backend image locally

```bash
cd /opt/nuujf/backend
docker build -t ghcr.io/YOUR_GITHUB_USER/nuujf_back:latest .
```

### 5b. Build the frontend image locally

```bash
cd /opt/nuujf/frontend
docker build --build-arg VITE_API_BASE_URL=https://YOUR_API_DOMAIN -t ghcr.io/YOUR_GITHUB_USER/jbnuu_front:latest .
```

The `--build-arg` bakes the API URL into the compiled JavaScript. Vite replaces `import.meta.env.VITE_API_BASE_URL` at build time — there's no runtime config for this.

### 5c. Start everything

```bash
cd /opt/nuujf/backend
docker compose -f docker-compose.prod.yml up -d
```

### 5d. Verify all containers are healthy

```bash
docker compose -f docker-compose.prod.yml ps
```

You should see five containers. `db` and `redis` should say `healthy`. `web`, `telegram-bot`, and `frontend` should say `running`:

```
NAME                    STATUS              PORTS
backend-db-1            Up (healthy)
backend-redis-1         Up (healthy)
backend-web-1           Up          127.0.0.1:8000->8000/tcp
backend-telegram-bot-1  Up
backend-frontend-1      Up          127.0.0.1:3000->80/tcp
```

If `web` keeps restarting, check `docker compose -f docker-compose.prod.yml logs web`. The most common cause is a wrong `DB_PASSWORD` or `REDIS_URL` in `.env`.

### 5e. Verify Redis is working

**Why:** Redis is the Django cache backend. If it's misconfigured, every cached view and session will fail silently or throw 500 errors.

```bash
# Check Redis directly:
docker compose -f docker-compose.prod.yml exec redis redis-cli -a YOUR_REDIS_PASSWORD ping
# Expected output: PONG

# Check Django can talk to Redis:
docker compose -f docker-compose.prod.yml exec web python manage.py shell -c "
from django.core.cache import cache
cache.set('deploy_test', 'ok', 30)
result = cache.get('deploy_test')
print(f'Redis test: {result}')
assert result == 'ok', 'Redis connection failed!'
"
```

### 5f. Verify database migrations ran

The `entrypoint.sh` runs `python manage.py migrate --noinput` automatically on container start, but verify it worked:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py showmigrations | grep '\[ \]'
```

If this outputs nothing, all migrations are applied. If it lists unapplied migrations, run:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
```

### 5g. Verify static files were collected

```bash
ls /var/www/nuujf/static/ | head -20
```

You should see Django/Wagtail admin static files. If the directory is empty:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput --clear
```

---

## 6. Create the superadmin user

**Why:** This is the account you'll use to log into the Wagtail CMS admin panel (`/admin/`) and the Django admin (`/django-admin/`). Without it, there's no way to manage content.

```bash
cd /opt/nuujf/backend
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

It will prompt for username, email, and password interactively. Use a strong password — this account has full control over the CMS.

**To change the password later:**

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py changepassword admin
```

**To create additional staff users programmatically:**

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_user('editor', 'editor@YOUR_DOMAIN', 'strong_password_here', is_staff=True)
print('Editor user created')
"
```

---

## 7. Install and configure Nginx with SSL

**Why:** Nginx is the only process that faces the internet. It terminates SSL, serves static files from disk, and reverse-proxies everything else to the Docker containers. The Docker ports are bound to `127.0.0.1` — they are invisible from outside the server.

### 7a. Install Nginx and Certbot

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo systemctl enable nginx
```

### 7b. Set up temporary Nginx config for SSL certificate issuance

Certbot needs to verify you own the domain by serving a file over HTTP. We need a minimal Nginx config first:

```bash
sudo tee /etc/nginx/sites-available/nuujf.uz.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN www.YOUR_DOMAIN YOUR_API_DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Nginx is working. SSL pending.\n';
        add_header Content-Type text/plain;
    }
}
EOF
```

```bash
sudo mkdir -p /var/www/certbot
sudo ln -sf /etc/nginx/sites-available/nuujf.uz.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 7c. Obtain SSL certificates

```bash
sudo certbot --nginx \
  -d YOUR_DOMAIN \
  -d www.YOUR_DOMAIN \
  -d YOUR_API_DOMAIN \
  --non-interactive \
  --agree-tos \
  -m YOUR_EMAIL
```

Verify the certificate:

```bash
sudo certbot certificates
```

Verify auto-renewal works:

```bash
sudo certbot renew --dry-run
```

### 7d. Deploy the full production Nginx config

Now replace the temporary config with the real one from the repo:

```bash
sudo cp /opt/nuujf/backend/nginx/nuujf.uz.conf /etc/nginx/sites-available/nuujf.uz.conf
```

The config in `nginx/nuujf.uz.conf` does the following:

| URL pattern                  | What happens                                         |
|-----------------------------|------------------------------------------------------|
| `http://*`                  | 301 redirect to `https://`                           |
| `https://YOUR_DOMAIN/*`     | Proxied to frontend container on `127.0.0.1:3000`    |
| `https://YOUR_API_DOMAIN/static/*` | Served directly from `/var/www/nuujf/static/`  |
| `https://YOUR_API_DOMAIN/media/*`  | Served directly from `/var/www/nuujf/media/`   |
| `https://YOUR_API_DOMAIN/*` | Proxied to Django/Gunicorn on `127.0.0.1:8000`       |

Test and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 7e. Verify everything works end-to-end

```bash
# Frontend loads:
curl -sI https://YOUR_DOMAIN | head -5

# API responds:
curl -sI https://YOUR_API_DOMAIN/api/schema/ | head -5

# Static files served by Nginx (check X-Served-By or response time):
curl -sI https://YOUR_API_DOMAIN/static/wagtailadmin/css/core.css | head -5

# Wagtail admin loads:
curl -sI https://YOUR_API_DOMAIN/admin/ | head -5
```

### 7f. Enable HSTS and SSL redirect

Now that SSL is confirmed working, update `.env` to enable the security headers:

```bash
cd /opt/nuujf/backend
nano .env
```

Change these values:

```env
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=63072000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

Restart the web container to pick up the changes:

```bash
docker compose -f docker-compose.prod.yml restart web
```

---

## 8. Configure the firewall

**Why:** Even though Docker ports are bound to localhost, it's defense-in-depth. Only SSH, HTTP, and HTTPS should be reachable from the internet.

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

Expected output should show only ports 22, 80, and 443 as ALLOW.

---

## 9. Set up CI/CD with GitHub Actions

**Why:** After the first manual deploy, every subsequent deploy should be automated. Push to `main` → tests run → Docker image built → pushed to GitHub Container Registry → server pulls and restarts. No SSH-ing in to deploy.

### 9a. How the pipelines work

**Backend pipeline** (`.github/workflows/deploy.yml` in `nuujf_back`):

```
push to main → [test] → [build-and-push] → [deploy via SSH]
                 │              │                    │
                 │              │                    └─ SSH to server, docker pull,
                 │              │                       restart web + bot, run migrations
                 │              └─ Build Docker image, push to ghcr.io
                 └─ Django check + migrate against real Postgres + Redis services
```

**Frontend pipeline** (`.github/workflows/deploy.yml` in `jbnuu_front`):

```
push to main → [lint+build] → [build-and-push] → [deploy via SSH]
                    │                 │                    │
                    │                 │                    └─ SSH to server, docker pull,
                    │                 │                       restart frontend container
                    │                 └─ Build Docker image with VITE_API_BASE_URL baked in
                    └─ npm ci, eslint, vite build
```

### 9b. Add GitHub Secrets

Go to **each repository → Settings → Secrets and variables → Actions** and add these secrets:

| Secret name       | Value                                                   |
|-------------------|---------------------------------------------------------|
| `SERVER_HOST`     | `YOUR_SERVER_IP`                                        |
| `SERVER_USER`     | `YOUR_DEPLOY_USER`                                      |
| `SERVER_SSH_KEY`  | Contents of `~/.ssh/id_ed25519` (the private key)       |
| `SERVER_PORT`     | `22` (or your custom SSH port)                          |

`GITHUB_TOKEN` is provided automatically — you don't need to create it.

### 9c. Set up the server to accept registry pulls

The CI/CD deploy step logs into GHCR from the server using `GITHUB_TOKEN`. For the first-time setup, verify Docker can pull from GHCR:

```bash
# Create a Personal Access Token at github.com/settings/tokens with `read:packages` scope
echo YOUR_PAT | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin
```

### 9d. Create a GitHub Environment for approval gates (optional)

Go to each repo → **Settings → Environments → New environment → "production"**. Enable "Required reviewers" if you want manual approval before each deploy.

### 9e. The CI/CD workflow files

The full working pipeline files are already in the repos:

- **Backend:** `.github/workflows/deploy.yml`
- **Frontend:** `.github/workflows/deploy.yml`

These are complete, working files — not skeletons. They use:
- `docker/setup-buildx-action@v3` for multi-platform builds
- `docker/login-action@v3` for GHCR authentication
- `docker/metadata-action@v5` for automatic `sha-<commit>` and `latest` tagging
- `docker/build-push-action@v5` with GitHub Actions cache (`type=gha`)
- `appleboy/ssh-action@v1.0.3` for SSH deployment

Every push to `main` produces two image tags:
- `sha-abc1234` — for precise rollback to any commit
- `latest` — always the newest successful build

---

## 10. Zero-downtime redeployment

**Why:** After CI/CD is set up, pushes to `main` trigger automatic deploys. But you'll sometimes need to redeploy manually (hotfix, env change, rollback). Here's how to do it without dropping requests.

### Automatic (push to main)

Just push your code. The CI/CD pipeline handles everything:

```bash
git push origin main
# Watch the pipeline at github.com/YOUR_GITHUB_USER/nuujf_back/actions
```

### Manual redeploy (backend)

```bash
cd /opt/nuujf/backend

# Pull the latest image without stopping anything
docker compose -f docker-compose.prod.yml pull web telegram-bot

# Replace the web container — Docker Compose starts the new one before killing the old
docker compose -f docker-compose.prod.yml up -d --no-deps web

# The bot doesn't serve HTTP so a regular restart is fine
docker compose -f docker-compose.prod.yml restart telegram-bot

# Run migrations in case the new image has schema changes
docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# Clean up old images
docker image prune -f
```

### Manual redeploy (frontend)

```bash
cd /opt/nuujf/backend

docker compose -f docker-compose.prod.yml pull frontend
docker compose -f docker-compose.prod.yml up -d --no-deps frontend
docker image prune -f
```

### Rollback to a previous version

Every deploy tags the image with `sha-<commit>`. To roll back:

```bash
# 1. Find the commit SHA you want to go back to:
docker images ghcr.io/YOUR_GITHUB_USER/nuujf_back --format "{{.Tag}}"

# 2. Edit .env and set:
#    IMAGE_TAG=sha-abc1234
nano /opt/nuujf/backend/.env

# 3. Pull and restart:
docker compose -f docker-compose.prod.yml pull web
docker compose -f docker-compose.prod.yml up -d --no-deps web

# 4. If the rollback involves a migration revert:
docker compose -f docker-compose.prod.yml exec web python manage.py migrate <app_name> <migration_number>
```

---

## 11. Database backups

### Manual backup

```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p /opt/nuujf/backups

docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U nuujf_user nuujf_db | gzip > /opt/nuujf/backups/nuujf_${TIMESTAMP}.sql.gz

echo "Backup saved: /opt/nuujf/backups/nuujf_${TIMESTAMP}.sql.gz"
```

### Automated daily backup via cron

```bash
crontab -e
```

Add this line (runs at 3 AM, keeps 30 days of backups):

```cron
0 3 * * * cd /opt/nuujf/backend && docker compose -f docker-compose.prod.yml exec -T db pg_dump -U nuujf_user nuujf_db | gzip > /opt/nuujf/backups/nuujf_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz && find /opt/nuujf/backups -name "*.sql.gz" -mtime +30 -delete
```

### Restore from backup

```bash
cd /opt/nuujf/backend

# Stop web and bot to prevent writes during restore
docker compose -f docker-compose.prod.yml stop web telegram-bot

# Drop and recreate the database
docker compose -f docker-compose.prod.yml exec -T db psql -U nuujf_user -c "DROP DATABASE IF EXISTS nuujf_db;"
docker compose -f docker-compose.prod.yml exec -T db psql -U nuujf_user -c "CREATE DATABASE nuujf_db;"

# Restore the backup
gunzip -c /opt/nuujf/backups/nuujf_20260430_030000.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db psql -U nuujf_user nuujf_db

# Restart services
docker compose -f docker-compose.prod.yml start web telegram-bot
```

---

## 12. Troubleshooting

### View logs

```bash
cd /opt/nuujf/backend

# Django/Gunicorn logs (most common):
docker compose -f docker-compose.prod.yml logs -f web

# Telegram bot:
docker compose -f docker-compose.prod.yml logs -f telegram-bot

# All services at once:
docker compose -f docker-compose.prod.yml logs -f

# Nginx (on host):
sudo tail -f /var/log/nginx/nuujf_backend_error.log
sudo tail -f /var/log/nginx/nuujf_frontend_error.log

# Django security middleware (IP blocks, suspicious requests):
tail -f /opt/nuujf/backend/logs/security.log
```

### Container keeps restarting

```bash
# Check the exit code and last logs:
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=50 web
```

Common causes:
- Wrong `DB_PASSWORD` → Gunicorn can't connect to Postgres → crash loop
- Wrong `REDIS_URL` → entrypoint.sh hangs waiting for Redis
- Missing `HEMIS_TOKEN` → Django settings crash on import

### 502 Bad Gateway from Nginx

The container behind Nginx isn't responding. Check:

```bash
# Is the container running?
docker compose -f docker-compose.prod.yml ps web

# Is Gunicorn actually listening?
curl -sI http://127.0.0.1:8000/ | head -3

# Check Nginx error log:
sudo tail -20 /var/log/nginx/nuujf_backend_error.log
```

### Redis NOAUTH error

Your `REDIS_URL` in `.env` doesn't include the password. It must be:
```
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@redis:6379/1
```
Note the colon before the password — that's the empty-username syntax for Redis URIs.

### Static files returning 404

```bash
# Are they on disk?
ls /var/www/nuujf/static/ | head

# If empty, re-collect:
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput --clear

# Verify Nginx config points to the right path:
grep -n "alias.*static" /etc/nginx/sites-available/nuujf.uz.conf
```

### Disk running out of space

```bash
# Check overall disk:
df -h /

# Docker is usually the culprit:
docker system df

# Remove unused images (safe):
docker image prune -a -f

# Nuclear option — remove everything unused (careful with volumes):
docker system prune -f
```

### Rebuild from scratch (last resort)

```bash
cd /opt/nuujf/backend
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### Quick reference card

```bash
# Status
docker compose -f docker-compose.prod.yml ps

# Restart one service
docker compose -f docker-compose.prod.yml restart web

# Django shell
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Database shell
docker compose -f docker-compose.prod.yml exec db psql -U nuujf_user -d nuujf_db

# Create another superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Flush Redis cache
docker compose -f docker-compose.prod.yml exec redis redis-cli -a YOUR_REDIS_PASSWORD -n 1 FLUSHDB

# Check deployment readiness
docker compose -f docker-compose.prod.yml exec web python manage.py check --deploy

# Resource usage
docker stats --no-stream
```

---

## 13. Security checklist

Run through this before going live:

- [ ] `DEBUG=False` in `.env`
- [ ] `SECRET_KEY` is random, 50+ characters, not the default
- [ ] `ALLOWED_HOSTS` lists only your actual domains
- [ ] `SECURE_SSL_REDIRECT=True` (after SSL is confirmed working)
- [ ] `SECURE_HSTS_SECONDS=63072000` (after SSL is confirmed working)
- [ ] `SESSION_COOKIE_SECURE=True` and `CSRF_COOKIE_SECURE=True`
- [ ] Redis has a password set via `REDIS_PASSWORD`
- [ ] PostgreSQL has a strong, unique password
- [ ] `.env` is in `.gitignore` and never committed
- [ ] Docker ports bound to `127.0.0.1`, not `0.0.0.0`
- [ ] UFW firewall enabled with only 22/80/443 open
- [ ] SSL certificate valid: `sudo certbot certificates`
- [ ] `python manage.py check --deploy` passes
- [ ] Automated backups running: `crontab -l`
- [ ] Log rotation configured for Nginx and Django logs
