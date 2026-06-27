# Roadmap

## Реализовано ✅

### Domain + Application слой

- [x] Модели: `User`, `Category`, `Item`, `Characteristic`, `Gallery`, `Tag`, `Comment`, `Rating`
- [x] Domain: Value Objects (`Name`, `Slug`, `Email`, `HashedPassword`, `Score`, `MarketplaceLink`)
- [x] Application: `UnitOfWork` Protocol
- [x] Application: use cases + DTOs для `auth`, `user`, `category`, `tag`, `item`, `comment`, `rating`, `upload`, `storage`, `blog`
- [x] Item.youtube_url — ссылка на YouTube-обзор
- [x] MarketplaceLink — ссылки на маркетплейсы (JSONB)
- [x] Item.view_count — счётчик просмотров (инкрементируется при `GET /items/{id}`, задаётся вручную через admin)
- [x] Characteristic.group — группировка характеристик

### Infrastructure слой

- [x] SQLAlchemy: модели + маперы + репозитории для всех модулей (user, category, item, tag, comment, rating, blog)
- [x] Alembic: все миграции применены
- [x] MinIO (S3-compatible): `MinIOFileStorage` (aioboto3), `StoragePort` Protocol
- [x] JWT: `JWTTokenService` (python-jose)
- [x] bcrypt: `BcryptHasher`
- [x] Presigned URLs: `GetPresignedUrlsUseCase`

### Presentation (FastAPI)

- [x] Роутеры + схемы для всех модулей
- [x] Item sub-resources: `/items/{id}/tags`, `/items/{id}/characteristics`, `/items/{id}/gallery`
- [x] Rate limiting (slowapi): `POST /auth/login`, `POST /auth/register` — 5/минуту
- [x] `GET /health` + `GET /api/v1/health`

### Blog-модуль

- [x] Domain: `BlogPost`, `BlogProductLink`, `BlogPostStatus` enum
- [x] CRUD постов: create, get, list, update, delete
- [x] Lifecycle: publish / unpublish / archive
- [x] Обложка: `POST /blog/posts/{slug}/cover` (upload в MinIO)
- [x] Теги блога: CRUD `BlogTag` + привязка к постам
- [x] Ссылки на товары: `BlogProductLink` (привязка/отвязка товаров к посту)
- [x] SEO-поля: `seo_title`, `seo_description`
- [x] Категории из каталога: `category_id` → `categories.id` (таблица `blog_categories` удалена)

### Frontend

- [x] Auth: login, register, profile, JWT refresh
- [x] Каталог: главная, catalog, item detail, tags, categories
- [x] Блог: список постов, детальная страница (markdown render)
- [x] Комментарии CRUD + рейтинг-виджет
- [x] Админ-панель: CRUD товаров, категорий, тегов, блог-постов
- [x] Presigned URLs: кэш через Next.js Redis CacheHandler (45 мин)

### DevOps

- [x] `docker-compose.yml` — dev-стек (postgres, minio, minio-init, backend, frontend)
- [x] `docker-compose.prod.yml` — prod-стек (+ nginx, без прямых портов)
- [x] `nginx/nginx.conf` + `nginx/conf.d/coremarket.conf` (HTTP)
- [x] `nginx/conf.d/coremarket-ssl.conf` (HTTPS + HSTS)
- [x] `scripts/init-letsencrypt.sh` — certbot

### Async Infrastructure (Фаза 11) ✅ 2026-06-24

- [x] `redis:7-alpine` — брокер + result backend, volume `redis_data`
- [x] `celery_worker` + `celery_beat` + `flower:5555` сервисы в docker-compose
- [x] `celery_app.py` — production Celery setup, 5 очередей (default/emails/images/search_sync/homepage), beat_schedule, JSON-логи
- [x] `tasks/notifications.py` — `send_welcome_email` (asyncio.run, SMTP-ready, 3 retries)
- [x] `tasks/ratings.py` — `recalculate_item_rating` (SQL AVG, idempotent)
- [x] `tasks/images.py` — `generate_thumbnail` (aioboto3 + Pillow, `thumb_<uuid>.jpg`)
- [x] `tasks/cleanup.py` — `cleanup_expired_sessions` (beat 2am UTC)
- [x] `tasks/search_sync.py` — `index_item`, `delete_item_from_index` (queue: search_sync)
- [x] `tasks/homepage.py` — `precompute_homepage_snapshot` → Redis (beat каждые 5 мин)
- [x] Интеграция: register → email, rating → recalc, upload → thumbnail, item CRUD → ES sync (все fire-and-forget)

### Observability — Grafana Loki (Фаза 12) ✅ 2026-06-26

- [x] `loki` + `promtail` сервисы в docker-compose
- [x] `grafana` сервис (порт 3001), автоматический provisioning datasources
- [x] Backend: структурированные JSON-логи (structlog + `logging_middleware.py`)
- [x] FastAPI middleware: логировать каждый запрос (latency, status, method, path)

### Observability — Prometheus + Tempo + OTel ✅ 2026-06-26

- [x] `metrics.py` — Prometheus registry: HTTP counter, histogram (p50/p95/p99), in-flight gauge
- [x] `MetricsMiddleware` — автоматический сбор HTTP метрик
- [x] `otel.py` — OpenTelemetry SDK: инструментирует FastAPI, SQLAlchemy, httpx
- [x] `LoggingMiddleware` — инжектирует `trace_id` + `span_id` в каждую лог-запись
- [x] `GET /metrics` endpoint (Prometheus scrape)
- [x] `prometheus` сервис (порт 9090, 15d retention, remote-write → Tempo)
- [x] `tempo` сервис (OTLP gRPC:4317, 72h retention, metrics-generator)
- [x] 5 Grafana дашбордов: API metrics, Celery, Redis, PostgreSQL, Infrastructure
- [x] Cross-data-source correlation: Loki → Tempo (trace drill-down)
- [x] Exporters: postgres-exporter, redis-exporter, elasticsearch-exporter, node-exporter, cadvisor

### Elasticsearch Search ✅ 2026-06-26

- [x] `elasticsearch:8.17.0` + `kibana:8.17.0` сервисы в docker-compose
- [x] Clean Architecture search subsystem: `search/domain/` + `search/application/` + `search/infrastructure/`
- [x] `SearchRepositoryProtocol` + `AutocompleteRepositoryProtocol` — domain Protocols
- [x] `ESItemSearchRepository` — реализует оба Protocol
- [x] Analyzers: `multilingual` (RU+EN stemmer+stopwords), `autocomplete_index` (edge_ngram min=2, max=20)
- [x] Popularity score: `rating * 0.6 + log1p(views) * 0.4`
- [x] `function_score`: text relevance + popularity boost
- [x] `fuzziness: AUTO` — typo tolerance
- [x] `GET /search/items` — full-text search с filters и ranking
- [x] `GET /search/suggestions` — autocomplete (edge ngram, real-time)
- [x] `POST /search/reindex` — admin-only full reindex
- [x] CLI: `python -m src.backend.scripts.reindex [--drop]`
- [x] Celery sync: item create/update/delete → ES (queue: search_sync)
- [x] `SEARCH_ENABLED` flag — SQL ILIKE fallback при `false`

### Frontend Performance ✅ 2026-06-25–26

- [x] Next.js 16 `'use cache'` + PPR (`cacheComponents: true`) на всех страницах
- [x] Redis Custom CacheHandler (`cache-handlers/redis-handler.js`) — db 1, base64 RSC payload
- [x] `generateStaticParams` на `/catalog/[category]`, `/tags/[slug]`, `/blog/[slug]`
- [x] `React.cache()` деduplication в 4 server component функциях
- [x] `api.get()` с `AbortSignal` для отмены in-flight запросов
- [x] Homepage: 4 cached Suspense sub-components + precomputed Redis snapshot
- [x] `GET /api/v1/homepage` — cache-first (Redis → live)

### Frontend Loading UX ✅ 2026-06-26

- [x] `.skeleton` CSS — shimmer sweep, заменяет `animate-pulse`
- [x] `NavigationProgress` — 2px route progress bar, event delegation, Bezier curve
- [x] `ItemCard` — shimmer плейсхолдер → fade-in (`opacity-0→100`, 500ms) по `onLoad`
- [x] 7 `loading.tsx` страниц — точные shimmer-скелеты реального layout
- [x] `prefers-reduced-motion` — все анимации accessibility-ready

### Production Optimization ✅ 2026-06-25

- [x] Security headers в Nginx (X-Frame-Options, X-Content-Type-Options, Permissions-Policy)
- [x] `sitemap.ts` — динамический XML sitemap (items, categories, tags, blog posts)
- [x] `robots.ts` — robots.txt
- [x] JSON-LD structured data: WebSite, Product, Article, BreadcrumbList
- [x] OG / Twitter Card metadata на всех страницах
- [x] Error boundaries в layout
- [x] `next/image` (Image) везде вместо `<img>` — LCP оптимизация
- [x] `fetchPriority="high"` на LCP-изображениях в GalleryViewer
- [x] `auth-context.tsx` — `useMemo`/`useCallback` для стабильного контекста

### Telegram Alerts ✅ 2026-06-28

- [x] `infrastructure/notifications/telegram.py` — `send_telegram_alert` (sync) + `async_send_telegram_alert` (async via executor)
- [x] Anti-spam: Redis db=2, ключ `tg:cd:{fingerprint}` (SHA256, 16 hex chars), TTL 300s; при недоступном Redis — alert всё равно отправляется
- [x] `main.py` → `_unhandled_exception_handler` — отправка алерта при любом HTTP 500
- [x] `celery_app.py` → `task_failure` сигнал — отправка алерта при сбое задачи (task_name + exception + retries)
- [x] Grafana Unified Alerting provisioning: `contact_points.yml`, `notification_policies.yml`, `alert_rules.yml`
  - **ВАЖНО:** `chatid` хардкодом в YAML как строка в кавычках, не через env var — Grafana парсит числа без кавычек как int → crash. Замените `"YOUR_CHAT_ID_HERE"` в `contact_points.yml` на свой chat ID перед деплоем.
- [x] 5 Grafana alert rules: HTTP 5xx rate, Celery failures, Loki ERROR spike, backend down, p95 latency
- [x] Config: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TELEGRAM_ALERTS_ENABLED` (default `false`)
- [x] Тесты: 50 passed (`tests/infrastructure/notifications/test_telegram.py`)
- [x] `docs/telegram-alerts.md` — setup guide, testing, troubleshooting

### Markdown Rendering ✅ 2026-06-28

- [x] Backend: mistune 3.x плагины `strikethrough`, `table`, `task_lists` подключены
- [x] Backend: `_SafeLinkRenderer` — внешние ссылки получают `target="_blank" rel="noopener noreferrer"`
- [x] Frontend: `MarkdownContent.tsx` — client component с `highlight.js` (hljs.highlightElement на `pre code`)
- [x] Frontend: `.prose` CSS написан вручную в `globals.css` (`@tailwindcss/typography` несовместим с Tailwind v4)
- [x] Frontend: блог-страница и admin preview используют `<MarkdownContent>` вместо `dangerouslySetInnerHTML`
- [x] Seed: 5 блог-постов с реальным markdown (таблицы, code blocks, strikethrough, task lists, blockquote)
- [x] Тесты: 33 → 53 passed (новые классы: Tables, Strikethrough, TaskLists, ExternalLinks)

### Тесты

- [x] 550+ тестов: domain (unit), presentation (интеграционные через httpx), tasks (unit + async), search (229 тестов), notifications (50), markdown (53) ✅ 2026-06-28
- [x] Покрытие: auth, user, category, tag, item, comment, rating, upload, tasks, search (application / query builders / sync+index / presentation API), notifications/telegram, markdown renderer
- [x] Search: `build_item_document` полностью покрыт (24 теста), `function_score` internals (factor/modifier/boost_mode/score_mode/prefix_length/min_should_match), ES exception → 503, validation 422s, bulk batching
- [x] Bugfix: `tests/presentation/item/conftest.py` — `view_count=0` в `GetItemResult` + `ItemListEntry` (11 тестов восстановлены)

---

## Следующие этапы

### Semantic Search — Vector Search

- [ ] Генерация embeddings для товаров (Sentence Transformers / OpenAI)
- [ ] Векторное хранилище (pgvector или Elasticsearch kNN)
- [ ] Гибридный поиск: BM25 (текущий) + cosine similarity (векторный)
- [ ] Семантический поиск: "водонепроницаемые наушники для спорта" → релевантные товары

### Recommendation Engine

- [ ] Collaborative filtering: "пользователи, просматривавшие X, также смотрели Y"
- [ ] Content-based: сходство по тегам, категории, характеристикам
- [ ] Celery задача: пересчёт рекомендаций по расписанию
- [ ] `GET /items/{id}/recommendations` endpoint

### AI Ranking & Personalization

- [ ] Learning-to-rank: CTR-сигналы (клики, время на странице, рейтинг)
- [ ] Персонализированная выдача по истории просмотров пользователя
- [ ] A/B тесты ранжирования через feature flags

### Аналитика и социальные функции

- [ ] Лайки на объекты
- [ ] Избранное (сохранённые товары)
- [ ] Лайки на комментарии
- [ ] In-app уведомления
- [ ] Email уведомления (Celery `emails` queue уже готов)
- [ ] User behavior analytics (просмотры, поиски, конверсии)
