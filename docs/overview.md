# CoreMarket — Обзор проекта

## Описание

Агрегатор обзоров от техно-блогеров. Блогер снимает ролик о товаре — товар добавляется на сайт с полной информацией, встроенным YouTube-обзором и ссылками на маркетплейсы.

Поддерживает карточки товаров, новостей, статей и других объектов.

## Функциональность

### Каталог и объекты

- Регистрация и аутентификация пользователей (JWT)
- Роли: Admin / User
- Категории и карточки объектов
- Краткое и полное описание
- Характеристики (с группировкой)
- YouTube-ссылка на обзор (встроенный плеер + кнопка перехода)
- Ссылки на маркетплейсы с ценами (DNS, Amazon, AliExpress, Wildberries и т.д.)
- Галерея изображений (хранение в MinIO / S3-compatible object storage)
- Теги (M2M к объектам)
- Комментарии (с вложенностью)
- Рейтинг объектов (оценка 1–5)
- Счётчик просмотров (`view_count`)

### Поиск

- **Elasticsearch full-text search** — RU+EN анализаторы, typo tolerance (fuzziness AUTO), relevance ranking с popularity boost
- **Autocomplete** — edge_ngram, real-time suggestions
- **SQL fallback** — ILIKE по title и short_description (когда ES недоступен)
- Фильтрация по категории, тегам, рейтингу
- Пагинация (limit / offset)

### Контент

- Блог-модуль (посты с markdown, теги, ссылки на товары, SEO-поля, статусы draft/published/archived)
- **Markdown rendering** — mistune 3.x с плагинами (таблицы, strikethrough, task lists), syntax highlighting (highlight.js), внешние ссылки `target="_blank"`
- Presigned URL для прямого доступа к файлам в MinIO
- Rate limiting на auth-эндпоинтах (slowapi)
- Админ-панель

### Инфраструктура

- **Celery 5 + Redis** — очередь асинхронных задач (email, thumbnails, search sync, homepage precompute)
- **Redis cache** — Next.js RSC кэш (db 1), homepage snapshot, presigned URLs (45 мин)
- **Homepage precomputation** — Celery beat обновляет Redis snapshot каждые 5 мин
- **ISR** — `generateStaticParams` на category/tag/blog страницах

### Observability

- **Prometheus** — метрики HTTP, Celery, Redis, PostgreSQL, Elasticsearch
- **Grafana** — 5 дашбордов (API metrics, Celery, Redis, Postgres, Infrastructure)
- **Loki + Promtail** — централизованный сбор логов из Docker-контейнеров
- **OpenTelemetry + Tempo** — distributed tracing, trace_id в логах, Grafana correlation
- **Telegram Alerts** — Python sender (Redis cooldown 5 мин) + Grafana Unified Alerting: 5 alert rules (5xx rate, Celery failures, ERROR log spike, backend down, p95 latency)

### Frontend UX

- Progressive loading: shimmer skeletons, route progress bar, image fade-in
- SEO: sitemap.xml, robots.txt, JSON-LD (WebSite/Product/Article/Breadcrumb), OG/Twitter metadata
- Error boundaries, loading.tsx на всех страницах
- Streaming через React `<Suspense>`

## Технологический стек

### Backend

| Технология          | Назначение                                        |
|---------------------|---------------------------------------------------|
| Python 3.13         | Основной язык                                     |
| FastAPI             | Веб-фреймворк                                     |
| PostgreSQL 17       | База данных                                       |
| SQLAlchemy          | Async ORM                                         |
| Alembic             | Миграции БД                                       |
| Pydantic v2         | Валидация данных / схемы                          |
| pydantic-settings   | Конфигурация через ENV                            |
| JWT (python-jose)   | Аутентификация                                    |
| bcrypt              | Хэширование паролей                               |
| MinIO               | Объектное хранилище (S3-compatible)               |
| aioboto3            | Async S3 клиент                                   |
| slowapi             | Rate limiting                                     |
| Celery 5            | Очередь асинхронных задач (5 очередей)            |
| Redis 7             | Celery broker/results + Next.js RSC cache         |
| Flower              | Мониторинг Celery задач и воркеров                |
| Pillow              | Обработка изображений (thumbnails)                |
| Elasticsearch 8.17  | Full-text search, autocomplete, typo tolerance    |
| OpenTelemetry       | Distributed tracing (FastAPI + SQLAlchemy + httpx)|
| Prometheus          | Метрики (HTTP, Celery, инфраструктура)            |
| Docker              | Контейнеризация                                   |
| Nginx               | Reverse proxy (prod)                              |

### Frontend

| Технология       | Назначение                                          |
|------------------|-----------------------------------------------------|
| Next.js 16       | React-фреймворк (App Router, PPR, 'use cache')      |
| React 19         | UI-библиотека                                       |
| TypeScript       | Типизация                                           |
| Tailwind CSS 4   | Стили                                               |
| Redis (db 1)     | Custom CacheHandler для Next.js RSC                 |

### Observability

| Технология            | Назначение                                        |
|-----------------------|---------------------------------------------------|
| Grafana 10.4.0        | Дашборды, алерты, log+trace correlation           |
| Loki                  | Агрегация логов из Docker                         |
| Promtail              | Сборщик Docker-логов → Loki                       |
| Prometheus            | Scrape: backend, exporters                        |
| Grafana Tempo 2.3.0   | Хранение OTel трейсов (OTLP gRPC, 72h retention) |
| postgres-exporter     | PostgreSQL метрики для Prometheus                 |
| redis-exporter        | Redis метрики для Prometheus                      |
| elasticsearch-exporter| Elasticsearch метрики для Prometheus              |
| node-exporter         | Host CPU/RAM/disk метрики                         |
| cAdvisor              | Container resource метрики                        |
