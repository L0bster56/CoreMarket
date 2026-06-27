# CoreMarket

A full-stack marketplace catalog built with **FastAPI** + **Next.js**. Supports products, articles, blog posts, categories, tags, comments, ratings, and full-text search.

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4, App Router |
| Database | PostgreSQL 17 |
| Object Storage | MinIO (S3-compatible) |
| Search | Elasticsearch 8.17 |
| Cache / Queue | Redis 7 |
| Background Tasks | Celery 5 (5 queues), Celery Beat, Flower |
| Reverse Proxy | Nginx 1.27 |
| Observability | Grafana, Loki, Promtail, Prometheus, Tempo (OpenTelemetry) |
| Alerting | Telegram Alerts via Grafana Unified Alerting (5 rules) |
| Containerisation | Docker Compose |

## Architecture

Clean Architecture: `domain/` → `application/` → `infrastructure/` → `api/`

- Business logic lives exclusively in use cases (`application/<module>/use_cases/`)
- Database queries live exclusively in repositories (`infrastructure/db/sqlalchemy/<module>/repository.py`)
- Use cases depend only on the `UnitOfWork` Protocol — fully decoupled from infrastructure
- Images are stored in MinIO; only the MinIO key is stored in PostgreSQL

```
CoreMarket/
├── backend/        # FastAPI application (Clean Architecture)
│   ├── src/backend/
│   │   ├── domain/         # Entities, value objects, domain exceptions
│   │   ├── application/    # Use cases, DTOs, interfaces
│   │   ├── infrastructure/ # SQLAlchemy, MinIO, Redis, Elasticsearch, Security
│   │   └── presentation/   # FastAPI routers, schemas, dependencies
│   ├── migrations/         # Alembic migrations
│   ├── tests/              # 450+ tests
│   └── seeds/              # Database seed data
├── frontend/       # Next.js 16 application
│   └── src/
│       ├── app/            # App Router pages
│       ├── components/     # Reusable UI components
│       ├── services/       # API service layer
│       └── lib/            # Utilities, auth context, server fetch
├── nginx/          # Nginx config (HTTP + HTTPS/SSL)
├── prometheus/     # Prometheus scrape config
├── grafana/        # Dashboards + provisioning + alert rules
├── loki/           # Log aggregation config
├── promtail/       # Log shipping config
├── tempo/          # Distributed tracing config
├── certbot/        # Let's Encrypt SSL (production)
├── docs/           # Project documentation
└── scripts/        # init-letsencrypt.sh
```

## Local Development Setup

### Prerequisites

- Docker 24+ and Docker Compose v2
- Git

### 1. Clone & Configure

```bash
git clone https://github.com/your-username/coremarket.git
cd coremarket

# Copy the env template and fill in values
cp .env.example .env
```

Edit `.env` — at minimum set:
- `POSTGRES_PASSWORD` — any strong password
- `JWT_SECRET` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` — any credentials
- `GRAFANA_ADMIN_PASSWORD` — your Grafana admin password

### 2. Start All Services

```bash
docker compose up -d
```

First startup takes a few minutes (Elasticsearch needs ~60s to become healthy).

### 3. Services

| Service | URL | Auth |
|---|---|---|
| Frontend | http://localhost:3000 | — |
| Backend API | http://localhost:8000/api/v1 | — |
| API Docs | http://localhost:8000/docs | — |
| MinIO API | http://localhost:9000 | `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` |
| MinIO Console | http://localhost:9001 | same |
| Grafana | http://localhost:3001 | admin / `GRAFANA_ADMIN_PASSWORD` |
| Prometheus | http://localhost:9090 | — |
| Kibana | http://localhost:5601 | — |
| Flower (Celery) | http://localhost:5555 | — |
| Tempo | http://localhost:3200 | via Grafana |

### 4. Create Admin User

```bash
docker compose exec backend python scripts/seeds/create_admin.py
```

### 5. Reindex Elasticsearch

```bash
# Via CLI
docker compose exec backend python -m src.backend.scripts.reindex

# Via API (requires admin token)
curl -X POST http://localhost:8000/api/v1/search/reindex \
  -H "Authorization: Bearer <admin_token>"
```

## Production Deploy

### 1. Server Requirements

- Ubuntu 22.04+ or Debian 12+
- 4 GB RAM minimum (8 GB recommended for Elasticsearch)
- Docker 24+ and Docker Compose v2
- Domain name with DNS pointing to the server

### 2. Clone & Configure

```bash
git clone https://github.com/your-username/coremarket.git
cd coremarket

cp .env.example .env
# Edit .env with production values — strong passwords, real domain, etc.
```

Key production env vars:
```env
POSTGRES_PASSWORD=<strong-random-password>
JWT_SECRET=<python -c "import secrets; print(secrets.token_hex(32))">
MINIO_ACCESS_KEY=<strong-key>
MINIO_SECRET_KEY=<strong-secret>
GRAFANA_ADMIN_PASSWORD=<strong-password>
PUBLIC_URL=https://yourdomain.com
NEXT_PUBLIC_SITE_URL=https://yourdomain.com
MINIO_PUBLIC_URL=https://yourdomain.com:9000   # or your storage subdomain
```

### 3. SSL (Let's Encrypt)

```bash
# Edit scripts/init-letsencrypt.sh — set your domain and email
chmod +x scripts/init-letsencrypt.sh
sudo ./scripts/init-letsencrypt.sh
```

Then in `docker-compose.prod.yml` uncomment the SSL Nginx config lines.

### 4. Deploy

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 5. Deployment Checklist

- [ ] `.env` filled with production values (no defaults like `password` or `admin`)
- [ ] `JWT_SECRET` is a strong random value (32+ hex chars)
- [ ] `GRAFANA_ADMIN_PASSWORD` changed from default
- [ ] `PUBLIC_URL` and `NEXT_PUBLIC_SITE_URL` set to your domain
- [ ] `MINIO_PUBLIC_URL` accessible from the internet (presigned URLs)
- [ ] DNS A record pointing to your server IP
- [ ] SSL certificates obtained via `init-letsencrypt.sh`
- [ ] Nginx SSL config uncommented in `docker-compose.prod.yml`
- [ ] All containers healthy: `docker compose ps`
- [ ] Migrations applied (runs automatically via entrypoint)
- [ ] Admin user created: `docker compose exec backend python scripts/seeds/create_admin.py`
- [ ] Elasticsearch reindexed: `POST /api/v1/search/reindex`
- [ ] Grafana accessible and dashboards loaded
- [ ] Telegram alerts configured (if using): update `chatid` in `grafana/provisioning/alerting/contact_points.yml`

## Telegram Alerts Setup

1. Create a bot: message `@BotFather` on Telegram → `/newbot` → copy the token
2. Get your chat ID: message `@userinfobot` → copy the `id` field
3. Set in `.env`:
   ```
   TELEGRAM_BOT_TOKEN=<your-token>
   TELEGRAM_CHAT_ID=<your-chat-id>
   TELEGRAM_ALERTS_ENABLED=true
   ```
4. Edit `grafana/provisioning/alerting/contact_points.yml` → set `chatid: "<your-chat-id>"` (must be a quoted string)

5 alert rules are preconfigured: HTTP 5xx spike, Celery failures, Backend ERROR log spike, Backend unreachable, High API latency (p95 > 2s).

## Observability

Grafana at `http://localhost:3001` includes 10 preconfigured dashboards:

| Dashboard | Covers |
|---|---|
| API Metrics | Request rate, latency, error rate |
| API Requests | Per-endpoint breakdown |
| Celery Metrics | Queue depths, task throughput |
| Celery Tasks Detail | Per-task timing |
| Containers Overview | Docker container resources |
| Errors Monitoring | Application error tracking |
| Infrastructure | CPU, RAM, disk via node-exporter |
| PostgreSQL | DB connections, query stats |
| Redis | Memory, hit rate, ops/sec |
| Security Events | Auth failures, rate limit hits |

Distributed traces are available in Grafana → Explore → Tempo.

## Running Tests

```bash
# Inside backend container
docker compose exec backend pytest tests/ -v

# Or locally (requires local Python 3.13 + dependencies)
cd backend
poetry install
pytest tests/ -v
```

450+ tests covering domain, application, infrastructure, and presentation layers.

## Documentation

| File | Description |
|---|---|
| [docs/overview.md](docs/overview.md) | Project description and stack |
| [docs/architecture.md](docs/architecture.md) | Folder structure, layers, search, images |
| [docs/models.md](docs/models.md) | All models with fields |
| [docs/api.md](docs/api.md) | All endpoints with methods and access levels |
| [docs/auth.md](docs/auth.md) | JWT, roles, security |
| [docs/celery.md](docs/celery.md) | Celery tasks, Redis, Flower, Beat |
| [docs/deployment.md](docs/deployment.md) | Docker, ENV variables, Nginx |
| [docs/telegram-alerts.md](docs/telegram-alerts.md) | Telegram alerts setup and troubleshooting |

## License

MIT
