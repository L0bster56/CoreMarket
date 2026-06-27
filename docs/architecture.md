# Архитектура проекта

## Структура директорий

```text
CoreMarket/
├── backend/
├── frontend/
├── nginx/
│   ├── nginx.conf
│   └── conf.d/
│       ├── coremarket.conf      ← HTTP (dev/prod без SSL)
│       └── coremarket-ssl.conf  ← HTTPS (prod с SSL)
├── prometheus/
│   └── prometheus.yml           ← scrape configs: backend, exporters
├── tempo/
│   └── tempo-config.yml         ← OTLP gRPC, 72h retention, metrics-generator
├── grafana/
│   ├── provisioning/
│   │   └── datasources/         ← Loki, Prometheus, Tempo (cross-links)
│   └── dashboards/              ← 5 JSON dashboards (API, Celery, Redis, Postgres, Infra)
├── media/                       ← legacy-папка (не используется в prod, хранение в MinIO)
├── docs/
├── docker-compose.yml           ← dev-стек (порты наружу, hot-reload)
└── docker-compose.prod.yml      ← prod-стек (nginx, без прямых портов)
```

---

## Backend — чистая архитектура

```text
backend/
├── src/backend/
│   ├── main.py                                         ← FastAPI app, CORS, rate limiter, роутеры, /metrics
│   ├── config.py                                       ← Settings (POSTGRES_*, JWT_*, MINIO_*, CORS_ORIGINS,
│   │                                                     ELASTICSEARCH_URL, SEARCH_ENABLED, OTEL_ENABLED)
│   ├── metrics.py                                      ← Prometheus registry (coremarket_ prefix)
│   ├── otel.py                                         ← OpenTelemetry setup, OTEL_ENABLED flag, graceful no-op
│   ├── celery_app.py                                   ← Celery setup, 5 queues, beat_schedule, Prometheus signals
│   │
│   ├── middleware/
│   │   ├── metrics_middleware.py                       ← HTTP counter/histogram/gauge
│   │   └── logging_middleware.py                       ← trace_id + span_id injection из OTel
│   │
│   ├── domain/                                         ← чистые бизнес-сущности, без зависимостей
│   │   ├── shared/
│   │   │   ├── entity.py                               ← BaseEntity (id: UUID)
│   │   │   ├── mixins.py                               ← TimestampMixin (created_at, updated_at)
│   │   │   ├── errors.py
│   │   │   ├── specification.py
│   │   │   ├── policy.py
│   │   │   └── value_objects/
│   │   │       ├── email/                              ← Email value object
│   │   │       └── name/                               ← Name value object
│   │   ├── user/
│   │   │   ├── entity.py                               ← User entity
│   │   │   ├── enums.py                                ← UserRole (admin, user)
│   │   │   └── value_objects/
│   │   │       ├── HashedPassword/
│   │   │       ├── AvatarUrl/
│   │   │       └── username/
│   │   ├── category/
│   │   │   ├── entity.py                               ← Category entity
│   │   │   └── value_objects/slug/                     ← Slug value object
│   │   ├── item/
│   │   │   ├── entity.py                               ← Item entity (title, description, view_count…)
│   │   │   ├── characteristic.py                       ← Characteristic entity (group, name, value)
│   │   │   ├── gallery.py                              ← Gallery entity (image_url = MinIO key)
│   │   │   └── value_objects/marketplace_link.py       ← MarketplaceLink (name, url, price)
│   │   ├── tag/
│   │   │   └── entity.py                               ← Tag entity (name, slug)
│   │   ├── comment/
│   │   │   └── entity.py                               ← Comment entity (parent_id, is_deleted)
│   │   ├── rating/
│   │   │   ├── entity.py                               ← Rating entity (score 1–5, item_id, user_id)
│   │   │   └── value_objects/score.py                  ← Score (валидация диапазона 1–5)
│   │   └── blog/
│   │       ├── entity.py                               ← BlogPost entity (title, slug, status…)
│   │       ├── product_link.py                         ← BlogProductLink (product_id, display_order)
│   │       ├── enums.py                                ← BlogPostStatus (draft/published/archived)
│   │       └── errors.py
│   │
│   ├── application/                                    ← бизнес-логика, валидация прав, use cases
│   │   ├── shared/
│   │   │   ├── errors.py                               ← NotFoundError, ConflictError, NotAuthorizedError, BadRequestError
│   │   │   └── interfaces/
│   │   │       └── uow.py                              ← UnitOfWork Protocol
│   │   ├── auth/
│   │   │   ├── use_cases/                              ← login_user.py, refresh_token.py, get_me.py
│   │   │   ├── dtos/
│   │   │   ├── interfaces/security/                    ← HasherPort, TokenServicePort
│   │   │   └── errors.py
│   │   ├── user/
│   │   │   ├── use_cases/                              ← create_user, get_by_id, update_user, delete_user…
│   │   │   └── dtos/
│   │   ├── category/
│   │   │   ├── use_cases/                              ← list, get, create, update, delete
│   │   │   └── dtos/
│   │   ├── item/
│   │   │   ├── use_cases/                              ← list, get (+ increment view_count), create, update, delete
│   │   │   │                                             add/remove tag, add/update/delete characteristic, add/delete gallery
│   │   │   ├── dtos/
│   │   │   └── repository.py                           ← ItemRepository, CharacteristicRepository, GalleryRepository protocols
│   │   ├── tag/
│   │   │   ├── use_cases/                              ← list, get, create, delete
│   │   │   └── dtos/
│   │   ├── comment/
│   │   │   ├── use_cases/                              ← list, get, create, update, delete (soft)
│   │   │   └── dtos/
│   │   ├── rating/
│   │   │   ├── use_cases/                              ← get, create, update, delete
│   │   │   ├── dtos/
│   │   │   └── repository.py
│   │   ├── upload/
│   │   │   └── upload_image.py                         ← UploadImageUseCase (валидация type/size, сохранить в MinIO)
│   │   ├── storage/
│   │   │   ├── use_cases/get_presigned_urls.py         ← GetPresignedUrlsUseCase
│   │   │   └── dtos/get_presigned_urls.py
│   │   ├── tasks/
│   │   │   ├── notifications.py                        ← send_welcome_email (3 retries, SMTP-ready)
│   │   │   ├── ratings.py                              ← recalculate_item_rating (SQL AVG, idempotent)
│   │   │   ├── images.py                               ← generate_thumbnail (aioboto3 + Pillow)
│   │   │   ├── cleanup.py                              ← cleanup_expired_sessions (beat 2am UTC)
│   │   │   ├── search_sync.py                          ← index_item, delete_item_from_index (Celery tasks)
│   │   │   └── homepage.py                             ← precompute_homepage_snapshot → Redis (beat 5min)
│   │   └── blog/
│   │       ├── use_cases/                              ← create, get, list, update, delete, publish,
│   │       │                                             unpublish, archive, add/remove tag, link/unlink product,
│   │       │                                             create/update/delete/list blog_tag
│   │       ├── dtos/
│   │       ├── repository.py                           ← BlogRepository, BlogTagRepository protocols
│   │       └── errors.py
│   │
│   ├── infrastructure/                                 ← адаптеры: БД, безопасность, хранилище
│   │   ├── db/
│   │   │   └── sqlalchemy/
│   │   │       ├── core/
│   │   │       │   ├── session.py                      ← create_async_engine + async_session
│   │   │       │   ├── uow.py                          ← SqlAlchemyUnitOfWork
│   │   │       │   ├── repository.py                   ← SqlAlchemyRepository (базовый CRUD)
│   │   │       │   ├── models.py                       ← Base declarative model
│   │   │       │   └── mixins.py                       ← UUIDMixin, TimeStampMixin, ActiveMixin
│   │   │       ├── user/
│   │   │       │   ├── model.py                        ← UserModel
│   │   │       │   ├── repository.py
│   │   │       │   └── mapper.py
│   │   │       ├── category/
│   │   │       │   ├── model.py
│   │   │       │   ├── repository.py
│   │   │       │   └── mapper.py
│   │   │       ├── item/
│   │   │       │   ├── model.py                        ← ItemModel, CharacteristicModel, GalleryModel, item_tags
│   │   │       │   ├── repository.py                   ← SqlAlchemyItemRepository (ILIKE, фильтры, increment_view_count)
│   │   │       │   │                                     SqlAlchemyCharacteristicRepository, SqlAlchemyGalleryRepository
│   │   │       │   └── mapper.py
│   │   │       ├── tag/
│   │   │       │   ├── model.py
│   │   │       │   ├── repository.py
│   │   │       │   └── mapper.py
│   │   │       ├── comment/
│   │   │       │   ├── model.py                        ← self-ref parent_id, is_deleted
│   │   │       │   ├── repository.py                   ← get_by_item, soft_delete
│   │   │       │   └── mapper.py
│   │   │       ├── rating/
│   │   │       │   ├── model.py                        ← UniqueConstraint(item_id, user_id)
│   │   │       │   ├── repository.py                   ← get_by_item_and_user, avg_by_item
│   │   │       │   └── mapper.py
│   │   │       └── blog/
│   │   │           ├── model.py                        ← BlogPostModel, BlogTagModel, BlogProductLinkModel, blog_post_tags
│   │   │           ├── repository.py                   ← SqlAlchemyBlogRepository, SqlAlchemyBlogTagRepository
│   │   │           └── mapper.py
│   │   ├── security/
│   │   │   ├── bcrypt/
│   │   │   │   └── hasher.py                           ← BcryptHasher (hash, verify)
│   │   │   └── jose/
│   │   │       └── token.py                            ← JWTTokenService (create, decode access/refresh)
│   │   ├── notifications/
│   │   │   └── telegram.py                             ← send_telegram_alert (sync) + async_send_telegram_alert
│   │   │                                                 Redis cooldown db=2, SHA256 fingerprint, retry 2x, never raises
│   │   └── storage/
│   │       ├── local.py                                ← LocalFileStorage (legacy, не используется в prod)
│   │       └── minio/
│   │           └── storage.py                          ← MinIOFileStorage (aioboto3, S3-compatible)
│   │
│   ├── search/                                         ← Elasticsearch subsystem (Clean Architecture)
│   │   ├── domain/
│   │   │   ├── models.py                               ← SearchHit, SearchResponse, SuggestionItem, SuggestionsResponse
│   │   │   ├── value_objects.py                        ← ItemSearchParams
│   │   │   └── repositories.py                         ← SearchRepositoryProtocol, AutocompleteRepositoryProtocol
│   │   ├── application/
│   │   │   └── use_cases/
│   │   │       ├── search_items.py                     ← SearchItemsUseCase
│   │   │       └── autocomplete.py                     ← AutocompleteUseCase
│   │   └── infrastructure/
│   │       └── elasticsearch/
│   │           ├── client.py                           ← AsyncElasticsearch singleton
│   │           ├── indexes/
│   │           │   ├── base.py                         ← BaseIndex ABC
│   │           │   └── items.py                        ← RU+EN analyzers, edge_ngram mappings
│   │           ├── queries/
│   │           │   └── items.py                        ← build_item_search_query(), build_autocomplete_query()
│   │           ├── repositories/
│   │           │   └── item_search.py                  ← ESItemSearchRepository (implements both Protocols)
│   │           └── sync/
│   │               └── item_sync.py                    ← build_item_document(), index_item(), bulk_reindex()
│   │
│   └── presentation/
│       └── api/
│           └── v1/
│               ├── core/
│               │   ├── dependencies.py                 ← get_uow, UoWDep, get_current_user, require_admin
│               │   ├── schemas.py                      ← ExceptionSchema
│               │   ├── limiter.py                      ← slowapi limiter (rate limiting)
│               │   └── handlers/
│               │       └── exceptions.py               ← NotFound→404, Conflict→409, NotAuthorized→403, JWT→401
│               ├── auth/
│               │   ├── router.py                       ← POST /auth/register|login|refresh|logout (rate limited)
│               │   ├── dependencies.py                 ← AdminUserDep, CurrentUserDep
│               │   └── schemas.py
│               ├── user/
│               │   ├── router.py                       ← GET|PATCH /users/me, GET|DELETE /users/{id}
│               │   └── schemas.py
│               ├── category/
│               │   ├── router.py
│               │   └── schemas.py
│               ├── item/
│               │   ├── router.py                       ← GET|POST|PATCH|DELETE /items
│               │   │                                     POST|DELETE /items/{id}/tags
│               │   │                                     POST|PATCH|DELETE /items/{id}/characteristics
│               │   │                                     POST|DELETE /items/{id}/gallery
│               │   └── schemas.py
│               ├── tag/
│               │   ├── router.py                       ← GET|POST /tags, DELETE /tags/{id}
│               │   └── schemas.py
│               ├── comment/
│               │   ├── router.py
│               │   └── schemas.py
│               ├── rating/
│               │   ├── router.py
│               │   └── schemas.py
│               ├── upload/
│               │   ├── router.py                       ← POST /upload?section=items|categories|users (Admin)
│               │   └── schemas.py                      ← UploadResponse { key: string }
│               ├── storage/
│               │   ├── router.py                       ← POST /storage/presigned-urls
│               │   ├── dependencies.py
│               │   └── schemas.py
│               ├── search/
│               │   ├── router.py                       ← GET /search/items, GET /search/suggestions, POST /search/reindex
│               │   ├── dependencies.py                 ← SearchUseCaseDep, AutocompleteUseCaseDep
│               │   └── schemas.py
│               ├── homepage/
│               │   └── router.py                       ← GET /homepage (cache-first: Redis → live)
│               └── blog/
│                   ├── router.py                       ← GET|POST|PATCH|DELETE /blog/posts
│                   │                                     publish/unpublish/archive, cover upload
│                   │                                     tags, products
│                   │                                     GET|POST|PATCH|DELETE /blog/tags
│                   ├── dependencies.py
│                   └── schemas.py

├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                                       ← Alembic миграции
├── scripts/
│   └── seeds/
│       └── create_admin.py                             ← создание первого admin-пользователя
│   └── reindex.py                                      ← CLI: python -m src.backend.scripts.reindex [--drop]
├── tests/
│   ├── domain/                                         ← юнит-тесты domain-слоя
│   ├── application/                                    ← юнит-тесты use cases
│   ├── presentation/                                   ← интеграционные тесты роутеров (httpx + TestClient)
│   └── search/                                         ← тесты поисковой инфраструктуры
├── pyproject.toml
├── alembic.ini
├── .env
└── Dockerfile
```

---

## Слоистая архитектура (Backend)

```
presentation/api/v1  (router + schemas)
        ↓
application          (use cases)          ← бизнес-логика, проверка прав
        ↓
infrastructure       (repository)         ← SQL запросы через SQLAlchemy
        ↓
domain               (entity + value obj) ← чистая бизнес-модель, нет зависимостей
```

**Правила:**
- Логика только в use cases (`application/<module>/use_cases/`)
- SQL-запросы только в репозиториях (`infrastructure/db/sqlalchemy/<module>/repository.py`)
- Use case зависит только от `UnitOfWork` Protocol
- Storage зависит только от `StoragePort` Protocol (`MinIOFileStorage` реализует его)

---

## Frontend Architecture

```text
frontend/
├── src/
│   ├── app/                         ← Next.js App Router pages
│   │   ├── layout.tsx               ← root layout: Providers, NavigationProgress, Header, Footer
│   │   ├── page.tsx                 ← homepage: static hero + 4 cached Suspense sub-components
│   │   ├── loading.tsx              ← shimmer skeleton (точный layout: hero + categories + cards + blog)
│   │   ├── sitemap.ts               ← dynamic XML sitemap
│   │   ├── robots.ts                ← robots.txt
│   │   ├── catalog/
│   │   │   ├── page.tsx             ← dynamic (searchParams), CatalogSidebar cached
│   │   │   └── [category]/          ← generateStaticParams pre-built, 'use cache'
│   │   ├── items/[id]/              ← force-dynamic (view_count accuracy)
│   │   ├── tags/[slug]/             ← generateStaticParams pre-built, 'use cache'
│   │   └── blog/
│   │       ├── page.tsx             ← BlogSidebar cached, BlogPostsList dynamic
│   │       └── [slug]/              ← generateStaticParams pre-built, 'use cache'
│   ├── components/
│   │   ├── ui/
│   │   │   ├── ItemCard.tsx         ← 'use client', image blur fade-in (shimmer → opacity transition)
│   │   │   ├── NavigationProgress.tsx ← 2px route progress bar, event delegation, Suspense wrapper
│   │   │   ├── StarRating.tsx
│   │   │   ├── SearchBar.tsx        ← Server Component
│   │   │   ├── GalleryViewer.tsx    ← fetchPriority="high" на первое изображение
│   │   │   ├── CommentsSection.tsx  ← 'use client', local state, initialComments={[]}
│   │   │   ├── RatingWidget.tsx     ← optimistic update
│   │   │   ├── MarkdownContent.tsx  ← 'use client', highlight.js на pre code, external links target="_blank"
│   │   │   └── RecommendedProducts.tsx ← serverGetPresignedUrls → RecommendationCard
│   │   └── layout/
│   │       ├── Header.tsx           ← useMemo/useCallback, Suspense wrapper
│   │       └── Footer.tsx
│   ├── lib/
│   │   ├── api.ts                   ← fetch client: Bearer токен, refresh-on-401, AbortSignal
│   │   ├── auth-context.tsx         ← React Context + useMemo, user/token/login/logout
│   │   └── server-fetch.ts          ← serverGet<T>() для Server Components
│   └── services/                    ← auth, categories, tags, items, ratings, comments, upload, blog, storage
├── cache-handlers/
│   └── redis-handler.js             ← Custom CacheHandler: Redis db 1, base64 RSC payload, graceful fallback
├── globals.css                      ← .skeleton (shimmer), .animate-content-appear, .progress-growing
└── next.config.ts                   ← cacheComponents: true (PPR), cacheLife profiles, Redis cacheHandler
```

### SSR / ISR Strategy

| Страница              | Режим                        | Кэш                                   |
|-----------------------|------------------------------|---------------------------------------|
| `/`                   | Static shell + streaming     | Sub-components: Redis 1h / catalog    |
| `/catalog`            | Dynamic (searchParams)       | Sidebar: Redis hours                  |
| `/catalog/[category]` | ISR + generateStaticParams   | Redis catalog (5min)                  |
| `/items/[id]`         | Dynamic (`force-dynamic`)    | Presigned URLs: Redis 45min           |
| `/tags/[slug]`        | ISR + generateStaticParams   | Redis hours                           |
| `/blog`               | Dynamic (searchParams)       | Sidebar: Redis hours                  |
| `/blog/[slug]`        | ISR + generateStaticParams   | Redis hours                           |

### Redis Frontend Cache

- **Cache handler:** `cache-handlers/redis-handler.js` — Next.js Custom CacheHandler
- **Redis DB:** `redis db 1` (db 0 зарезервирован для Celery)
- **Key prefix:** `nextjs:cache:`
- **Presigned URLs:** кэшируются 45min (MinIO выдаёт TTL 2h, запас для пересборки)
- **Graceful fallback:** если `REDIS_URL` не задан — файловый кэш Next.js без изменений

### Loading UX

- **`.skeleton`** — shimmer sweep (800px gradient, 1.6s ease-in-out) заменяет `animate-pulse` везде
- **`NavigationProgress`** — 2px progress bar top-0 z-[9999], запускается кликом по `<a>`, останавливается при `pathname` change
- **`ItemCard` fade-in** — shimmer-плейсхолдер → `opacity-0→100` за 500ms по `onLoad`
- **`loading.tsx`** — 7 страниц со скелетами, точно повторяющими реальный layout
- **`prefers-reduced-motion`** — все анимации соблюдают accessibility

### Homepage Optimization

- Статичный hero рендерится мгновенно (нет запросов)
- 4 async sub-components (`HeroBadge`, `CategoriesSection`, `TrendingSection`, `BlogPreviewSection`) в `<Suspense>`
- Каждый sub-component кэширован отдельно (`'use cache'`) с разными TTL
- Backend: `GET /api/v1/homepage` возвращает precomputed snapshot из Redis (beat обновляет каждые 5 мин)
- Inline Suspense-скелеты с shimmer пока данные стримятся

---

## Search Architecture

### Elasticsearch Subsystem

Поисковая инфраструктура построена поверх **Elasticsearch 8.17** со Clean Architecture изоляцией.

```
Presentation  →  Application (SearchItemsUseCase / AutocompleteUseCase)
                       ↓
               Domain (SearchRepositoryProtocol)
                       ↑
              Infrastructure (ESItemSearchRepository)
```

### Index Features

- **Analyzers:** `multilingual` (RU+EN stemmer + stopwords), `autocomplete_index` (edge_ngram min=2, max=20)
- **Typo tolerance:** `fuzziness: AUTO` в search-запросах
- **Relevance ranking:** `function_score` = text relevance + popularity boost
- **Popularity score:** `rating * 0.6 + log1p(views) * 0.4`

### Sync Strategy

```
POST/PATCH /items   →  Celery task: index_item       (queue: search_sync)
DELETE /items/{id}  →  Celery task: delete_item_from_index (queue: search_sync)
CLI reindex         →  python -m src.backend.scripts.reindex [--drop]
```

`SEARCH_ENABLED=true/false` — флаг в `config.py`; при `false` все sync-задачи пропускаются.

### Endpoints

| Эндпоинт                       | Описание                                        |
|--------------------------------|-------------------------------------------------|
| `GET /search/items`            | Full-text search: fuzziness, filters, ranking   |
| `GET /search/suggestions`      | Autocomplete (edge ngram, real-time)            |
| `POST /search/reindex`         | Admin-only: полный переиндекс всех товаров      |

### SQL Fallback

`SqlAlchemyItemRepository` по-прежнему поддерживает `ILIKE` поиск — используется когда `SEARCH_ENABLED=false` или ES недоступен.

---

## Observability Stack

### Общая схема

```
FastAPI app
  ├── /metrics                    ← Prometheus scrape endpoint
  ├── MetricsMiddleware           ← HTTP counter / histogram / in-flight gauge
  └── LoggingMiddleware           ← trace_id + span_id в каждом лог-записи
        ↓
   OpenTelemetry SDK              ← инструментирует FastAPI, SQLAlchemy, httpx
        ↓
   Tempo (OTLP gRPC:4317)         ← хранение трейсов, 72h retention
        ↓
   Grafana                        ← дашборды, алерты, log→trace correlation
```

```
Docker logs (stdout JSON)
   ↓
Promtail                          ← docker driver, com_docker_compose_service label
   ↓
Loki                              ← агрегация логов
   ↓
Grafana                           ← log drill-down, correlation с Prometheus + Tempo
```

### Prometheus Metrics

Центральный реестр в `backend/src/backend/metrics.py` (префикс `coremarket_`):

| Метрика                                  | Тип       | Описание                           |
|------------------------------------------|-----------|------------------------------------|
| `coremarket_http_requests_total`         | Counter   | По method, endpoint, status        |
| `coremarket_http_request_duration_seconds` | Histogram | Латентность (p50/p95/p99)         |
| `coremarket_http_requests_in_progress`   | Gauge     | Активные запросы                   |

Scrape targets в `prometheus.yml`: backend, node-exporter, cadvisor, postgres-exporter, redis-exporter, elasticsearch-exporter.

### Grafana Dashboards

| Dashboard              | Содержимое                                                  |
|------------------------|-------------------------------------------------------------|
| `api-metrics.json`     | Requests/s, p50/p95/p99, error rate, top slow endpoints     |
| `celery-metrics.json`  | Task throughput, duration by task, failures per queue       |
| `redis-metrics.json`   | Hit/miss rate, memory usage, ops/sec, command breakdown     |
| `postgres-metrics.json`| Connections, cache hit %, txns/s, dead tuples, locks        |
| `infrastructure.json`  | Host CPU/RAM/disk + container CPU/mem/network (cadvisor)    |

### Distributed Tracing

- OTel SDK инструментирует FastAPI (каждый HTTP запрос = span), SQLAlchemy (каждый SQL), httpx
- `trace_id` + `span_id` инжектируются в Loki-логи через `LoggingMiddleware`
- Grafana: Loki → "View in Tempo" drill-down (cross-data-source links)
- `OTEL_ENABLED=false` — graceful no-op fallback без изменения кода

### Telegram Alerts

Два независимых пути доставки алертов:

```
Backend 500          →  main.py _unhandled_exception_handler
Celery task failure  →  celery_app.py task_failure signal
                                ↓
                   infrastructure/notifications/telegram.py
                   ├── Redis db=2: cooldown check (SHA256 fingerprint, 300s TTL)
                   └── httpx POST → Telegram Bot API (retry 2x, timeout 5s)

Grafana alert fires  →  Grafana Unified Alerting
                        └── contact_points.yml → Telegram contact point
```

| Alert rule           | Trigger                                | Cooldown |
|----------------------|----------------------------------------|----------|
| Python (backend)     | Unhandled HTTP 500                     | 5 min    |
| Python (Celery)      | Task failure signal                    | 5 min    |
| `cm-http-5xx-rate`   | 5xx rate > 0.05 req/s за 5 мин        | 4 h      |
| `cm-celery-task-failures` | > 0 failures за 5 мин            | 4 h      |
| `cm-loki-error-spike`| > 5 ERROR-логов за 5 мин (Loki)       | 4 h      |
| `cm-backend-down`    | `up` < 1 за 2 мин                     | 4 h      |
| `cm-high-request-latency` | p95 > 2s за 5 мин               | 4 h      |

Подробнее: [docs/telegram-alerts.md](telegram-alerts.md)

---

## Async Architecture

### Celery Configuration

5 изолированных очередей для независимого масштабирования:

| Очередь       | Задачи                                             | Приоритет |
|---------------|----------------------------------------------------|-----------|
| `default`     | Общие задачи                                       | Normal    |
| `emails`      | `send_welcome_email` (SMTP, 3 retries)             | High      |
| `images`      | `generate_thumbnail` (Pillow + aioboto3)           | Normal    |
| `search_sync` | `index_item`, `delete_item_from_index`             | Normal    |
| `homepage`    | `precompute_homepage_snapshot` (beat 5 мин)        | Low       |

Worker слушает все 5 очередей через `-Q` флаг. Beat (`celery_beat`) управляет периодическими задачами.

### Интеграция с бизнес-логикой

```
POST /auth/register    →  send_welcome_email.delay()        (fire-and-forget)
POST /items/{id}/rating →  recalculate_item_rating.delay()  (fire-and-forget)
POST /upload           →  generate_thumbnail.delay()        (fire-and-forget)
POST/PATCH /items      →  index_item.delay()                (search_sync queue)
DELETE /items/{id}     →  delete_item_from_index.delay()    (search_sync queue)
Beat schedule (2am UTC) →  cleanup_expired_sessions
Beat schedule (5 min)   →  precompute_homepage_snapshot → Redis
```

### Мониторинг

- **Flower** (порт 5555): веб-интерфейс задач, воркеров, очередей, retry-статистики
- **Grafana `celery-metrics.json`**: Prometheus-метрики от Celery Prometheus signals

---

## Performance Architecture

### Redis Cache Layers

| Слой                     | Redis DB | Ключ                            | TTL         |
|--------------------------|----------|---------------------------------|-------------|
| Celery broker/results    | db 0     | celery-task-meta-*              | по задаче   |
| Next.js RSC cache        | db 1     | `nextjs:cache:*`                | по странице |
| Presigned URLs           | db 1     | через Next.js CacheHandler      | 45 min      |
| Homepage snapshot        | db 0     | `homepage:snapshot`             | 10 min      |
| Telegram cooldown        | db 2     | `tg:cd:{fingerprint}`           | 300s        |

### Homepage Precomputation

- Celery beat каждые 5 минут запускает `precompute_homepage_snapshot`
- Задача собирает trending items, categories, blog preview → сериализует в JSON → Redis
- `GET /api/v1/homepage`: сначала `Redis.get("homepage:snapshot")`, при miss — live query
- Frontend: sub-components обращаются к `/api/v1/homepage`, результат кэшируется в Next.js Redis (db 1)

### ISR / Static Generation

- `generateStaticParams` на `/catalog/[category]`, `/tags/[slug]`, `/blog/[slug]`
- При deploy: все published posts и активные categories/tags pre-built как static HTML
- Revalidation: через `cacheTag` инвалидацию при CRUD операциях через admin

### Request-Level Caching

- `React.cache()` дедуплицирует запросы внутри одного render-pass
- `api.get()` с `AbortSignal` для отмены in-flight запросов при навигации
- Server Components → `serverGet<T>()` с встроенным Next.js fetch dedup

---

## Рейтинг — логика работы

| Действие                  | Эндпоинт                      | Доступ        |
|---------------------------|-------------------------------|---------------|
| Получить средний рейтинг  | `GET /items/{id}/rating`       | Public        |
| Поставить оценку (1–5)    | `POST /items/{id}/rating`      | User (auth)   |
| Изменить свою оценку      | `PATCH /items/{id}/rating`     | User (owner)  |
| Убрать свою оценку        | `DELETE /items/{id}/rating`    | User (owner)  |

**Ответ `GET /items/{id}/rating`:**
```json
{
  "average": 4.3,
  "count": 12,
  "user_score": 5
}
```
`user_score` — оценка текущего пользователя (null если гость или не оценивал).

**Ограничения:**
- Один пользователь — одна оценка на объект (`UniqueConstraint item_id + user_id`)
- Среднее вычисляется на уровне репозитория (`AVG(score)`)

---

## Поиск и фильтрация

**SQL (fallback / `SEARCH_ENABLED=false`):** `SqlAlchemyItemRepository`:

- **Поиск:** `ILIKE '%query%'` по полям `name` (title), `short_description`
- **Фильтрация:** по `category_id`, `tag` (slug), `min_rating`, `is_published`
- **Пагинация:** `limit` + `offset` параметры в query string

**Elasticsearch (primary, `SEARCH_ENABLED=true`):** `ESItemSearchRepository`:

- Full-text search по title, description, tags (RU+EN анализаторы)
- `fuzziness: AUTO` (typo tolerance)
- `function_score` с popularity boost
- Autocomplete через `edge_ngram`

---

## Изображения — MinIO (S3-compatible)

Все медиафайлы хранятся в MinIO. В PostgreSQL хранится только **MinIO-ключ** (строка без хоста).

| Раздел (`section`) | MinIO-ключ (пример)                          | Где используется            |
|--------------------|----------------------------------------------|-----------------------------|
| `items`            | `items/550e8400-e29b-41d4-a716-446655440000.jpg` | `Gallery.image_url`       |
| `categories`       | `categories/abc-123.png`                     | `Category.image_url`        |
| `users`            | `users/avatar-uuid.jpg`                      | `User.avatar_url`           |
| `blog`             | `blog/cover-uuid.jpg`                        | `BlogPost.cover_image_url`  |

**Workflow загрузки:**
1. `POST /upload?section=items` (multipart) → MinIOFileStorage → возвращает `key`
2. Сохранить `key` в нужное поле (`gallery.image_url`, `category.image_url` и т.д.)
3. Для отображения: `POST /storage/presigned-urls` с массивом ключей → получить presigned URL (TTL 3600s)
4. Frontend кэширует presigned URLs в Redis 45 мин (`serverGetPresignedUrls`)

**Docker:** `MINIO_ENDPOINT=http://minio:9000` (внутренний), `MINIO_PUBLIC_URL=http://localhost:9000` (для presigned URL доступных снаружи).

Бакет `coremarket` создаётся автоматически сервисом `minio-init` при старте контейнеров.
