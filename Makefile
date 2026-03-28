# ──────────────────────────────────────────────────────────────
# Makefile — Server management commands for nuujf
# Usage: make <command>
# ──────────────────────────────────────────────────────────────

# Docker compose command prefix
DC = docker compose
WEB = $(DC) exec web

# ══════════════════════════════════════════════════════════════
# 🚀 DEPLOYMENT
# ══════════════════════════════════════════════════════════════

## Build and start all services
up:
	$(DC) up -d --build

## Start services (without rebuilding)
start:
	$(DC) up -d

## Stop all services
stop:
	$(DC) down

## Restart all services
restart:
	$(DC) down
	$(DC) up -d

## Rebuild and restart only the web + bot (no DB/Redis restart)
redeploy:
	$(DC) up -d --build web telegram-bot

# ══════════════════════════════════════════════════════════════
# 🗄️  DATABASE
# ══════════════════════════════════════════════════════════════

## Run database migrations
migrate:
	$(WEB) python manage.py migrate --noinput

## Create new migrations from model changes
makemigrations:
	$(WEB) python manage.py makemigrations

## Show migration status
showmigrations:
	$(WEB) python manage.py showmigrations

## Open Django database shell
dbshell:
	$(WEB) python manage.py dbshell

## Dump data to JSON backup file
dumpdata:
	$(WEB) python manage.py dumpdata --natural-foreign --natural-primary --indent 2 > data.json
	@echo "✅ Data exported to data.json"

## Load data from JSON backup file
loaddata:
	docker cp data.json $$($(DC) ps -q web):/app/data.json
	$(WEB) python manage.py loaddata /app/data.json
	@echo "✅ Data imported from data.json"

# ══════════════════════════════════════════════════════════════
# 👤 USER MANAGEMENT
# ══════════════════════════════════════════════════════════════

## Create a Django superuser (interactive)
createsuperuser:
	$(WEB) python manage.py createsuperuser

## Change password for a user (pass USER=username)
changepassword:
	$(WEB) python manage.py changepassword $(USER)

# ══════════════════════════════════════════════════════════════
# 📦 STATIC FILES
# ══════════════════════════════════════════════════════════════

## Collect static files
collectstatic:
	$(WEB) python manage.py collectstatic --noinput --clear

# ══════════════════════════════════════════════════════════════
# 🔍 DEBUGGING & LOGS
# ══════════════════════════════════════════════════════════════

## View web service logs (follow mode)
logs:
	$(DC) logs -f web

## View telegram bot logs
logs-bot:
	$(DC) logs -f telegram-bot

## View all service logs
logs-all:
	$(DC) logs -f

## Open Django shell
shell:
	$(WEB) python manage.py shell

## Open bash inside the web container
bash:
	$(WEB) bash

## Check deployment readiness
check:
	$(WEB) python manage.py check --deploy

# ══════════════════════════════════════════════════════════════
# 🧹 CLEANUP
# ══════════════════════════════════════════════════════════════

## Stop everything and remove volumes (⚠️  DELETES ALL DATA)
clean:
	@echo "⚠️  This will DELETE all data (database, redis, media)!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	$(DC) down -v --remove-orphans

## Remove dangling Docker images
prune:
	docker image prune -f

# ══════════════════════════════════════════════════════════════
# 📋 STATUS
# ══════════════════════════════════════════════════════════════

## Show running containers
ps:
	$(DC) ps

## Show container resource usage
stats:
	docker stats --no-stream $$($(DC) ps -q)

# ══════════════════════════════════════════════════════════════
# 🎯 QUICK SETUP (first time on a new server)
# ══════════════════════════════════════════════════════════════

## Full first-time setup: build → migrate → collectstatic → createsuperuser
setup: up
	@echo "⏳ Waiting for services to be healthy..."
	@sleep 10
	$(WEB) python manage.py migrate --noinput
	$(WEB) python manage.py collectstatic --noinput --clear
	$(WEB) python manage.py createsuperuser
	@echo ""
	@echo "✅ Setup complete! Visit http://localhost:8000"

# ══════════════════════════════════════════════════════════════
# 📖 HELP
# ══════════════════════════════════════════════════════════════

## Show this help message
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════╗"
	@echo "║        nuujf — Server Management Commands       ║"
	@echo "╚══════════════════════════════════════════════════╝"
	@echo ""
	@echo "  🚀 DEPLOYMENT"
	@echo "    make up              Build and start all services"
	@echo "    make start           Start services (no rebuild)"
	@echo "    make stop            Stop all services"
	@echo "    make restart         Restart all services"
	@echo "    make redeploy        Rebuild web + bot only"
	@echo ""
	@echo "  🗄️  DATABASE"
	@echo "    make migrate         Run migrations"
	@echo "    make makemigrations  Create new migrations"
	@echo "    make showmigrations  Show migration status"
	@echo "    make dbshell         Open database shell"
	@echo "    make dumpdata        Export data to data.json"
	@echo "    make loaddata        Import data from data.json"
	@echo ""
	@echo "  👤 USERS"
	@echo "    make createsuperuser Create admin user"
	@echo "    make changepassword USER=admin"
	@echo ""
	@echo "  📦 STATIC"
	@echo "    make collectstatic   Collect static files"
	@echo ""
	@echo "  🔍 DEBUGGING"
	@echo "    make logs            Web service logs"
	@echo "    make logs-bot        Telegram bot logs"
	@echo "    make logs-all        All service logs"
	@echo "    make shell           Django shell"
	@echo "    make bash            Bash in web container"
	@echo "    make check           Deployment check"
	@echo ""
	@echo "  🧹 CLEANUP"
	@echo "    make clean           Stop + delete all data"
	@echo "    make prune           Remove dangling images"
	@echo ""
	@echo "  📋 STATUS"
	@echo "    make ps              Show running containers"
	@echo "    make stats           Container resource usage"
	@echo ""
	@echo "  🎯 FIRST TIME"
	@echo "    make setup           Full initial setup"
	@echo ""

.PHONY: up start stop restart redeploy migrate makemigrations showmigrations \
        dbshell dumpdata loaddata createsuperuser changepassword collectstatic \
        logs logs-bot logs-all shell bash check clean prune ps stats setup help

.DEFAULT_GOAL := help
