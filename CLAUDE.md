# CoreMarket — Контекст проекта

## Что это

Fullstack каталог: FastAPI бэкенд + Next.js фронтенд. Поддерживает товары, новости, статьи и карточки объектов с категориями, тегами, комментариями и рейтингом.

## Структура репозитория

```
CoreMarket/
├── backend/        ← FastAPI приложение (Python 3.13)
├── frontend/       ← Next.js 16 приложение (TypeScript + Tailwind 4)
├── nginx/          ← Nginx конфигурация (HTTP + HTTPS)
├── media/          ← legacy-папка (prod хранилище — MinIO)
└── docs/           ← вся документация проекта
```

## Статус фаз

| Фаза | Описание | Статус |
|---|---|---|
| 1 | Frontend — все страницы и компоненты на mock данных | ✅ |
| 2 | Backend — Domain + Application слои (сущности, use cases, DTOs, UoW) | ✅ |
| 3 | Frontend — Auth-flow, контекст, валидация форм | ✅ |
| 4 | Frontend — Админ-панель CRUD формы, toast, upload-превью | ✅ |
| 5 | Backend — Infrastructure (SQLAlchemy, Security, Storage, Upload) | ✅ |
| 6 | Backend — FastAPI presentation layer (роутеры, схемы, main.py) | ✅ |
| 7A | Frontend — API-слой + auth (api.ts, services, auth-context, login, profile) | ✅ |
| 7B | Frontend — публичный каталог (home, catalog, item detail, tags) | ✅ |
| 7C | Frontend — комментарии CRUD + рейтинг-виджет + admin panel | ✅ |
| MinIO | Объектное хранилище (aioboto3, S3-compatible, docker-compose) | ✅ |
| Blog | Блог-модуль: посты, теги, продукт-линки, markdown, admin CRUD | ✅ |
| 10 | Деплой — Nginx + Docker Compose (production-ready стек) | ✅ |
| 12 | Observability — Grafana Loki + Promtail | ✅ |
| 11 | Celery + Redis — асинхронные задачи | ✅ |
| Alerts | Telegram Alerts — Python sender + Grafana Unified Alerting (5 rules) | ✅ |
| MD | Markdown rendering — mistune plugins, highlight.js, prose CSS вручную | ✅ |

## Документация

Перед началом работы читай `docs/`:

| Файл | Содержимое |
|---|---|
| [docs/overview.md](docs/overview.md) | Описание проекта и стек |
| [docs/architecture.md](docs/architecture.md) | Структура папок, слои, поиск, изображения |
| [docs/models.md](docs/models.md) | Все модели с полями |
| [docs/api.md](docs/api.md) | Все эндпоинты с методами и доступами |
| [docs/auth.md](docs/auth.md) | JWT, роли, безопасность |
| [docs/celery.md](docs/celery.md) | Celery задачи, Redis, Flower, Beat, логирование |
| [docs/deployment.md](docs/deployment.md) | Docker, ENV переменные, Nginx |
| [docs/roadmap.md](docs/roadmap.md) | Статус задач и план |
| [docs/tasks.md](docs/tasks.md) | Все задачи по 5 фазам (чеклист) |
| [docs/style.md](docs/style.md) | Backend code style (Python/FastAPI) |
| [docs/frontend-style.md](docs/frontend-style.md) | Frontend UI/UX style guide (компоненты, анимации, loading UX) |
| [docs/telegram-alerts.md](docs/telegram-alerts.md) | Telegram уведомления: setup, testing, troubleshooting |

## Frontend — стек и ключевые файлы

**Стек:** Next.js 16.2.6, React 19, TypeScript, Tailwind CSS 4, App Router.

**Запуск (dev):** `docker compose up -d` → frontend: http://localhost:3000, backend: http://localhost:8000/api/v1

**Страницы:** `/` главная, `/catalog` каталог+фильтры, `/catalog/[category]`, `/items/[id]` детальная карточка, `/tags/[slug]`, `/blog` список постов, `/blog/[slug]` пост, `/login`, `/register`, `/profile`, `/admin`, `/admin/blog`.

**Ключевые файлы:**
- `src/types/index.ts` — все TypeScript типы
- `src/lib/api.ts` — базовый fetch-клиент (Bearer токен, refresh-on-401)
- `src/lib/auth-context.tsx` — React Context: user, token, login, logout
- `src/lib/server-fetch.ts` — `serverGet<T>()` для Server Components
- `src/services/` — auth, categories, tags, items, ratings, comments, upload, blog
- `src/components/ui/` — ItemCard, CategoryCard, StarRating, SearchBar, GalleryViewer, CommentsSection, RatingWidget
- `src/components/layout/` — Header, Footer

## Ключевые решения

- **Архитектура:** Clean Architecture — `domain/` → `application/` → `infrastructure/` → `api/`. Логика только в use cases (`application/<module>/use_cases/`), запросы к БД только в репозиториях (`infrastructure/db/sqlalchemy/<module>/repository.py`). Use case зависит только от `UnitOfWork` Protocol.
- **Изображения:** хранятся в MinIO (S3-compatible). В PostgreSQL хранится только **MinIO-ключ** (`items/uuid.jpg`). Для получения URL — `POST /storage/presigned-urls`. `StoragePort` Protocol развязывает use case от реализации (`MinIOFileStorage`). В Docker: `MINIO_ENDPOINT=http://minio:9000`, `MINIO_PUBLIC_URL=http://localhost:9000`.
- **Поиск:** SQL ILIKE по `title` и `short_description`. Фильтрация по category_id, tag slug, min_rating. Пагинация: limit/offset.
- **Роли:** `admin` — полный CRUD. `user` — комментарии и рейтинг. Public — только чтение.
- **Социальные функции** (лайки, избранное, уведомления) — отложены, не реализовывать пока не попросят.

## Модели

`User`, `Category`, `Item`, `Characteristic`, `Gallery`, `Tag` (M2M с Item через `item_tags`), `Comment` (вложенность через `parent_id`, мягкое удаление), `Rating` (уникальный constraint `item_id + user_id`, score 1–5).

**Blog:** `BlogPost` (title, slug, content markdown, cover_image_url, `category_id` → `categories.id`, status: draft/published/archived, seo_title, seo_description), `BlogTag` (M2M с BlogPost через `blog_post_tags`), `BlogProductLink` (blog_post_id, product_id, display_order). Таблица `blog_categories` удалена — посты используют каталожные `Category` напрямую.
