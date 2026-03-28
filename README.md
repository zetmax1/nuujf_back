# NUUJF — University Backend

Django + Wagtail backend for the university website.

---

## 🚀 Deployment Guide (Step by Step)

### Prerequisites on the Server

- Ubuntu 20.04+ (or any Linux with Docker support)
- Docker & Docker Compose installed
- Git installed
- A domain name pointed to your server IP (e.g. `nuujf.uz`)

#### Install Docker (if not installed)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
docker compose version
```

---

### Step 1: Clone the Repository

```bash
# SSH into your server
ssh user@your-server-ip

# Clone the repo
git clone https://github.com/YOUR_USERNAME/nuujf.git /opt/nuujf
cd /opt/nuujf
```

---

### Step 2: Create the `.env` File

The `.env` file is NOT in the repository (it's in `.gitignore`). You must create it on the server:

```bash
nano .env
```

Paste and edit these values:

```env
# ─── Django Core ──────────────────────────────────────────────
SECRET_KEY=GENERATE_A_NEW_KEY_HERE
DEBUG=False
ALLOWED_HOSTS=nuujf.uz,www.nuujf.uz,YOUR_SERVER_IP
DJANGO_SETTINGS_MODULE=config.settings.production

# ─── Security ────────────────────────────────────────────────
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# ─── PostgreSQL ──────────────────────────────────────────────
DB_NAME=nuujf
DB_USER=nuujf_user
DB_PASSWORD=YOUR_STRONG_PASSWORD_HERE
DB_HOST=db
DB_PORT=5432

# ─── Redis ───────────────────────────────────────────────────
REDIS_URL=redis://redis:6379/1

# ─── API Keys ────────────────────────────────────────────────
HEMIS_TOKEN=your_hemis_token_here
```

> **💡 Generate a secure SECRET_KEY:**
> ```bash
> python3 -c "import secrets; print(secrets.token_urlsafe(50))"
> ```

> **💡 Generate a secure DB_PASSWORD:**
> ```bash
> python3 -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

---

### Step 3: Build and Start All Services

```bash
# First-time full setup (builds images, starts containers,
# runs migrations, collects static files, creates superuser)
make setup
```

This runs:
1. `docker compose up -d --build` — builds Docker images and starts all 4 services
2. Waits for PostgreSQL and Redis to be healthy
3. `python manage.py migrate` — creates all database tables
4. `python manage.py collectstatic` — collects static files
5. `python manage.py createsuperuser` — prompts you to create an admin account

---

### Step 4: Verify Everything is Running

```bash
# Check all containers are running
make ps

# Expected output:
# NAME                   STATUS
# nuujf-db-1             Up (healthy)
# nuujf-redis-1          Up (healthy)
# nuujf-web-1            Up
# nuujf-telegram-bot-1   Up

# Check logs for errors
make logs
```

---

### Step 5: Test the Application

```bash
# From the server itself
curl http://localhost:8000/admin/

# Or from your browser
# http://YOUR_SERVER_IP:8000/admin/
```

---

### Step 6: (Optional) Load Existing Data from SQLite

If you have data from a local SQLite database:

```bash
# ON YOUR LOCAL MACHINE: export data
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 \
    --exclude contenttypes --exclude auth.permission \
    --exclude wagtailcore.groupcollectionpermission \
    --exclude wagtailcore.grouppagepermission \
    --exclude sessions > data.json

# Copy to server
scp data.json user@your-server-ip:/opt/nuujf/

# ON THE SERVER: import data
make loaddata
```

---

## 🔄 Updating the Application (After Code Changes)

Every time you push new code and want to deploy:

```bash
# SSH into server
ssh user@your-server-ip
cd /opt/nuujf

# 1. Pull latest code
git pull origin main

# 2. Rebuild and restart web + bot (keeps DB and Redis running)
make redeploy

# 3. Run new migrations (if any)
make migrate

# 4. Collect static files (if any changed)
make collectstatic
```

Or as a one-liner:

```bash
git pull && make redeploy && make migrate && make collectstatic
```

---

## 📋 Quick Reference — All Make Commands

```
make help              Show all available commands

── DEPLOYMENT ──
make up                Build and start all services
make start             Start services (no rebuild)
make stop              Stop all services
make restart           Restart everything
make redeploy          Rebuild only web + bot

── DATABASE ──
make migrate           Run migrations
make makemigrations    Create new migration files
make showmigrations    Show migration status
make dbshell           Open PostgreSQL shell
make dumpdata          Export data → data.json
make loaddata          Import data ← data.json

── USERS ──
make createsuperuser   Create admin user
make changepassword USER=admin

── STATIC ──
make collectstatic     Collect static files

── DEBUGGING ──
make logs              Web service logs (follow)
make logs-bot          Telegram bot logs
make logs-all          All logs
make shell             Django Python shell
make bash              Bash inside web container
make check             Run deployment checks

── CLEANUP ──
make clean             ⚠️  Stop + DELETE all data
make prune             Remove unused Docker images

── STATUS ──
make ps                Show running containers
make stats             Container resource usage

── FIRST TIME ──
make setup             Full initial setup
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                 Docker Compose                   │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ PostgreSQL│  │  Redis   │  │  Telegram Bot  │  │
│  │  :5432    │  │  :6379   │  │  (polling)     │  │
│  └─────┬────┘  └────┬─────┘  └───────┬───────┘  │
│        │            │                │           │
│        └────────┬───┘                │           │
│                 │                    │           │
│          ┌──────┴──────┐             │           │
│          │   Django    │◄────────────┘           │
│          │  Gunicorn   │                         │
│          │   :8000     │                         │
│          └─────────────┘                         │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Container won't start
```bash
make logs              # Check for error messages
make ps                # Check container status
```

### Database connection error
```bash
# Verify DB is healthy
docker compose exec db pg_isready -U nuujf_user -d nuujf
```

### Permission denied on Docker
```bash
sudo usermod -aG docker $USER
# Then log out and back in
```

### Need to reset everything
```bash
make clean             # ⚠️  Deletes all data!
make setup             # Fresh start
```
