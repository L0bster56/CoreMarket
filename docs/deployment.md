# Деплой и конфигурация

## Запуск (разработка)

```bash
docker compose up -d
```

Сервисы:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001
- Flower (Celery мониторинг): http://localhost:5555
- Grafana: http://localhost:3001
- Kibana: http://localhost:5601
- Prometheus: http://localhost:9090
- Elasticsearch: http://localhost:9200
- Tempo: http://localhost:3200

## Запуск (production)

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Сервисы доступны через Nginx:
- Сайт: http://localhost (или ваш домен)
- API: http://localhost/api/v1/
- MinIO Console: http://localhost:9001 (прямой порт)

---

## ENV переменные

Создать файл `.env` в корне проекта (рядом с `docker-compose.yml`):

```env
# PostgreSQL
POSTGRES_USER=coremarket
POSTGRES_PASSWORD=secret
POSTGRES_DB=coremarket

# JWT
JWT_SECRET=your-very-secret-key-here

# MinIO
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=coremarket

# Prod: URL по которому MinIO доступен снаружи для presigned URLs
MINIO_PUBLIC_URL=http://localhost:9000

# Prod: публичный URL сайта (для CORS, NEXT_PUBLIC_API_URL, sitemap, OG-теги)
PUBLIC_URL=https://yourdomain.com
NEXT_PUBLIC_SITE_URL=https://yourdomain.com

# Redis / Celery
REDIS_URL=redis://redis:6379/0
CELERY_WORKER_CONCURRENCY=2

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200
ELASTICSEARCH_INDEX_PREFIX=coremarket
SEARCH_ENABLED=true

# OpenTelemetry (Tempo)
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317

# Grafana
GRAFANA_ADMIN_PASSWORD=admin

# Telegram Alerts (опционально)
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=987654321
TELEGRAM_ALERTS_ENABLED=false
```

Переменные `ASYNC_DATABASE_URL`, `DATABASE_URL`, `JWT_ACCESS_TOKEN_EXPIRES`, `JWT_REFRESH_TOKEN_EXPIRES`, `JWT_ALGORITHM`, `MINIO_ENDPOINT`, `CORS_ORIGINS`, `INTERNAL_API_URL`, `NEXT_PUBLIC_API_URL` задаются автоматически в `docker-compose.yml` из ENV выше.

Переменная `REDIS_URL=redis://redis:6379/1` для Next.js frontend задаётся в сервисе `frontend` внутри `docker-compose.yml` (отдельная Redis DB от Celery).

---

## Описание сервисов

### `docker-compose.yml` (dev)

#### Основные сервисы

| Сервис        | Image / Build               | Порты              | Описание                                                |
|---------------|-----------------------------|--------------------|--------------------------------------------------------|
| postgres      | postgres:17-alpine          | 5432:5432          | PostgreSQL с healthcheck                               |
| minio         | minio/minio:latest          | 9000:9000, 9001:9001| Объектное хранилище, Console на 9001                  |
| minio-init    | minio/mc:latest             | —                  | Создаёт бакет `coremarket` при старте                  |
| backend       | ./backend/Dockerfile        | 8000:8000          | FastAPI; depends_on: postgres, minio-init, redis, elasticsearch |
| frontend      | ./frontend/Dockerfile       | 3000:3000          | Next.js dev-сервер с hot-reload; depends_on: redis     |
| redis         | redis:7-alpine              | 6379:6379          | Celery broker (db 0) + Next.js RSC cache (db 1)        |

#### Async Infrastructure

| Сервис        | Image / Build               | Порты     | Описание                                               |
|---------------|-----------------------------|-----------|--------------------------------------------------------|
| celery_worker | ./backend/Dockerfile        | —         | Celery worker (5 очередей: default/emails/images/search_sync/homepage) |
| celery_beat   | ./backend/Dockerfile        | —         | Планировщик периодических задач (beat_schedule)        |
| flower        | ./backend/Dockerfile        | 5555:5555 | Мониторинг Celery; http://localhost:5555               |

#### Search

| Сервис          | Image                         | Порты     | Описание                                    |
|-----------------|-------------------------------|-----------|---------------------------------------------|
| elasticsearch   | elasticsearch:8.17.0          | 9200:9200 | Full-text search, autocomplete              |
| kibana          | kibana:8.17.0                 | 5601:5601 | ES Dev Tools, index management, Discover    |

#### Observability

| Сервис                | Image                                               | Порты              | Описание                                      |
|-----------------------|-----------------------------------------------------|--------------------|-----------------------------------------------|
| loki                  | grafana/loki:2.9.0                                  | 3100               | Агрегация логов (внутренний)                  |
| promtail              | grafana/promtail:2.9.0                              | —                  | Docker-логи → Loki; docker.sock mount         |
| grafana               | grafana/grafana:10.4.0                              | 3001:3000          | 5 дашбордов; http://localhost:3001            |
| prometheus            | prom/prometheus:v2.48.0                             | 9090:9090          | Scrape backend + exporters; 15d retention     |
| tempo                 | grafana/tempo:2.3.0                                 | 3200:3200, 4317:4317 | OTel OTLP gRPC, трейсы, 72h retention      |
| postgres-exporter     | prometheuscommunity/postgres-exporter:v0.15.0       | —                  | PostgreSQL → Prometheus метрики               |
| redis-exporter        | oliver006/redis_exporter:v1.55.0                    | —                  | Redis → Prometheus метрики                    |
| elasticsearch-exporter| prometheuscommunity/elasticsearch-exporter:v1.7.0   | —                  | ES → Prometheus метрики                       |
| node-exporter         | prom/node-exporter:v1.7.0                           | —                  | Host CPU/RAM/disk → Prometheus                |
| cadvisor              | gcr.io/cadvisor/cadvisor:v0.47.2                    | —                  | Container resources → Prometheus (privileged) |

### `docker-compose.prod.yml` (override)

Добавляет сервис `nginx`, убирает прямые порты у backend и frontend.

| Сервис    | Image                       | Порты          | Описание                             |
|-----------|-----------------------------|----------------|--------------------------------------|
| nginx     | nginx:1.27-alpine           | 80:80, 443:443 | Reverse proxy + SSL                  |
| postgres  | —                           | без портов     | Только внутри сети                   |
| backend   | —                           | без портов     | Только внутри сети                   |
| frontend  | ./frontend/Dockerfile.prod  | без портов     | Next.js standalone build             |
| minio     | —                           | 9000:9000      | MinIO API (9001 Console закрыт)      |

---

## Nginx

Оба варианта конфига — альтернативы: монтируется **одна** из папок целиком как `/etc/nginx/conf.d`
(директорией, не отдельным файлом — иначе `git pull`, который заменяет файл через rename,
не подхватится в уже запущенном контейнере без `--force-recreate`).

### HTTP (dev/prod без SSL): `nginx/conf.d/http/coremarket.conf`

```
location /api/   → proxy_pass http://backend:8000
location /       → proxy_pass http://frontend:3000
```

Включены security headers (`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`),
кэш для статики (`expires 30d`), `client_max_body_size 10m`.

### HTTPS (prod с SSL): `nginx/conf.d/ssl/coremarket-ssl.conf`

- `listen 443 ssl http2`
- HTTP → HTTPS редирект (301) для доменов; для запросов по голому IP сервера (несовпавший `Host`) —
  отдельный `default_server` на порту 80, проксирующий `/grafana/` на Grafana (доступ к дашбордам не по домену)
- HSTS: `max-age=31536000; includeSubDomains`
- TLS 1.2/1.3

Сертификат: Let's Encrypt через `scripts/init-letsencrypt.sh`.

Для включения SSL: в `docker-compose.prod.yml` раскомментировать строки с `nginx/conf.d/ssl` и `certbot`.

После правки любого файла в `nginx/conf.d/ssl/` на сервере — `git pull`, затем перечитать конфиг без даунтайма:
```bash
docker exec coremarket-nginx-1 nginx -t && docker exec coremarket-nginx-1 nginx -s reload
```

---

## Alembic — миграции

```bash
# Применить все миграции (внутри backend-контейнера)
docker compose exec backend alembic upgrade head

# Создать новую миграцию
docker compose exec backend alembic revision --autogenerate -m "описание"
```

В `docker-compose.yml` backend-контейнер запускает `alembic upgrade head` автоматически через entrypoint.

---

## Создание admin-пользователя

```bash
docker compose exec backend python scripts/seeds/create_admin.py
```

---

## Elasticsearch — управление

- **Kibana Dev Tools:** http://localhost:5601 — управление индексами, тестирование запросов
- **Полный переиндекс:** `POST /api/v1/search/reindex` (требует admin токен)
- **CLI переиндекс:**
  ```bash
  docker compose exec backend python -m src.backend.scripts.reindex
  docker compose exec backend python -m src.backend.scripts.reindex --drop  # удалить и пересоздать индекс
  ```
- **Отключение поиска:** `SEARCH_ENABLED=false` — все sync-задачи пропускаются, используется SQL ILIKE

---

## MinIO — управление

- **Console (dev):** http://localhost:9001 (логин: `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY`)
- Бакет `coremarket` создаётся автоматически сервисом `minio-init`
- Bucket policy: `none` (приватный) — доступ через presigned URLs
- Данные хранятся в Docker volume `minio_data`

---

## Observability — доступ

| Сервис     | URL (dev)               | Логин/Пароль             |
|------------|-------------------------|--------------------------|
| Grafana    | http://localhost:3001   | admin / `GRAFANA_ADMIN_PASSWORD` |
| Prometheus | http://localhost:9090   | без авторизации           |
| Kibana     | http://localhost:5601   | без авторизации (dev)     |
| Flower     | http://localhost:5555   | без авторизации (dev)     |
| Tempo      | http://localhost:3200   | через Grafana datasource  |

Grafana автоматически подключает datasources Loki, Prometheus, Tempo и загружает все 5 дашбордов через provisioning.

**Production:** прямой порт `3001` у Grafana закрыт (`docker-compose.prod.yml` сбрасывает `ports`). Доступ — через nginx по **IP сервера** на `http://<server-ip>/grafana/`, а не по домену: `nginx/conf.d/ssl/coremarket-ssl.conf` содержит отдельный `server { listen 80 default_server; server_name _; }`, который проксирует запросы `/grafana/` с несовпавшим `Host` (в т.ч. голый IP) на `grafana:3000/grafana/`. Домены (`sanjaranvarov.uz`, `api.sanjaranvarov.uz`) по-прежнему обслуживаются доменными server-блоками и редиректятся на HTTPS.

Grafana запущена с `GF_SERVER_SERVE_FROM_SUB_PATH=true` и `GF_SERVER_ROOT_URL=${GRAFANA_ROOT_URL}` — переменную `GRAFANA_ROOT_URL` в `.env` на сервере нужно выставить в `http://<server-ip>/grafana/`, иначе статика/редиректы Grafana будут ломаться.

---

## Redis — изоляция баз

| Redis DB | Использование                          |
|----------|----------------------------------------|
| db 0     | Celery broker + result backend         |
| db 1     | Next.js RSC cache (homepage snapshot, presigned URLs, страницы) |
| db 2     | Telegram alert cooldown (ключи `tg:cd:*`, TTL 300s) |

---

## Telegram Alerts — настройка

1. Создать бота: написать `@BotFather` → `/newbot` → скопировать токен
2. Получить chat ID: написать `@userinfobot` → скопировать поле `id`
3. В `.env` задать:
   ```
   TELEGRAM_BOT_TOKEN=<токен>
   TELEGRAM_CHAT_ID=<chat-id>
   TELEGRAM_ALERTS_ENABLED=true
   ```
4. **Обязательно** — обновить `chatid` в `grafana/provisioning/alerting/contact_points.yml`:
   ```yaml
   chatid: "YOUR_ACTUAL_CHAT_ID"   # ← заменить, в кавычках (строка)
   ```
   > Grafana не поддерживает env-var substitution для числовых значений в YAML.
   > `chatid` должен быть строкой (в кавычках), иначе Telegram-интеграция упадёт.

---

## Production Deployment Checklist

- [ ] `.env` заполнен production-значениями (никаких дефолтов: `password`, `admin`, `minioadmin`)
- [ ] `JWT_SECRET` — сильный случайный ключ: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] `GRAFANA_ADMIN_PASSWORD` изменён
- [ ] `PUBLIC_URL` и `NEXT_PUBLIC_SITE_URL` → ваш домен
- [ ] `MINIO_PUBLIC_URL` → публичный URL MinIO (доступен из браузера для presigned URLs)
- [ ] DNS A-запись указывает на IP сервера
- [ ] SSL-сертификаты получены через `scripts/init-letsencrypt.sh`
- [ ] SSL-конфиг в `docker-compose.prod.yml` раскомментирован
- [ ] Все контейнеры здоровы: `docker compose ps`
- [ ] Миграции применены (автоматически через entrypoint)
- [ ] Admin-пользователь создан: `docker compose exec backend python scripts/seeds/create_admin.py`
- [ ] Elasticsearch переиндексирован: `POST /api/v1/search/reindex`
- [ ] `GRAFANA_ROOT_URL` в `.env` выставлен на `http://<server-ip>/grafana/`
- [ ] Grafana открывается по `http://<server-ip>/grafana/` (порт 3001 наружу не открыт), дашборды загружены
- [ ] Telegram alerts настроены (если используются): обновлён `chatid` в `contact_points.yml`
- [ ] Log rotation включён (настроен в `docker-compose.yml` через `x-logging`)
