# API Endpoints

Base URL: `/api/v1`

---

## Health

| Метод | Путь             | Описание         | Доступ |
|-------|------------------|------------------|--------|
| GET   | `/health`        | Проверка статуса | Public |
| GET   | `/api/v1/health` | Проверка статуса | Public |

**Ответ:**
```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Авторизация `/auth`

| Метод | Путь             | Описание                     | Доступ |
|-------|------------------|------------------------------|--------|
| POST  | `/auth/register` | Регистрация пользователя     | Public |
| POST  | `/auth/login`    | Получить JWT токен           | Public |
| POST  | `/auth/refresh`  | Обновить токен               | Public |
| POST  | `/auth/logout`   | Выйти (инвалидировать токен) | User   |

> Rate limiting: `POST /auth/login` и `POST /auth/register` — лимит 5 запросов/минуту.

**Побочный эффект `POST /auth/register`:** запускает Celery-задачу `send_welcome_email` (fire-and-forget, очередь `emails`). HTTP-ответ не ждёт отправки письма.

---

## Пользователи `/users`

| Метод  | Путь          | Описание               | Доступ |
|--------|---------------|------------------------|--------|
| GET    | `/users/me`   | Профиль текущего юзера | User   |
| PATCH  | `/users/me`   | Обновить профиль       | User   |
| GET    | `/users/{id}` | Профиль пользователя   | Admin  |
| DELETE | `/users/{id}` | Удалить пользователя   | Admin  |

---

## Категории `/categories`

| Метод  | Путь               | Описание               | Доступ |
|--------|--------------------|------------------------|--------|
| GET    | `/categories`      | Получить все категории | Public |
| GET    | `/categories/{id}` | Получить категорию     | Public |
| POST   | `/categories`      | Создать категорию      | Admin  |
| PATCH  | `/categories/{id}` | Обновить категорию     | Admin  |
| DELETE | `/categories/{id}` | Удалить категорию      | Admin  |

---

## Объекты `/items`

### Поля объекта

#### `POST /items` — создание

| Поле                | Тип                             | Обязательное | Описание                                               |
|---------------------|---------------------------------|--------------|--------------------------------------------------------|
| `title`             | string                          | да           | Название                                               |
| `category_id`       | UUID                            | да           | ID категории                                           |
| `short_description` | string                          | да           | Краткое описание                                       |
| `description`       | string                          | да           | Полное описание                                        |
| `youtube_url`       | string \| null                  | нет          | Ссылка на YouTube-обзор                                |
| `marketplace_links` | `[{name, url, price?}]`         | нет          | Ссылки на маркетплейсы                                 |

#### `PATCH /items/{id}` — обновление

Все поля опциональны. Передаются только изменяемые поля.

| Поле                | Тип                             | Описание                                               |
|---------------------|---------------------------------|--------------------------------------------------------|
| `title`             | string \| null                  | Название                                               |
| `short_description` | string \| null                  | Краткое описание                                       |
| `description`       | string \| null                  | Полное описание                                        |
| `category_id`       | UUID \| null                    | ID категории                                           |
| `youtube_url`       | string \| null                  | Ссылка на YouTube-обзор                                |
| `marketplace_links` | `[{name, url, price?}]` \| null | Ссылки на маркетплейсы                                 |
| `is_published`      | bool \| null                    | Флаг публикации (Admin)                                |
| `view_count`        | int \| null                     | Счётчик просмотров (≥ 1, Admin). Ручная установка      |

**Пример PATCH с установкой view_count:**
```json
PATCH /api/v1/items/550e8400-e29b-41d4-a716-446655440000
{
  "view_count": 1500
}
```

> `view_count` ≥ 1. Значение `0` вернёт `422 Unprocessable Entity`.

**Побочный эффект `POST` и `PATCH /items`:** при `SEARCH_ENABLED=true` запускается Celery-задача `index_item_task` (очередь `search_sync`). HTTP-ответ не ждёт индексации.

**Побочный эффект `DELETE /items/{id}`:** при `SEARCH_ENABLED=true` запускается `delete_item_task` (очередь `search_sync`).

### Параметры запроса `GET /items`

| Параметр      | Тип     | Описание                                 |
|---------------|---------|------------------------------------------|
| `search`      | string  | Поиск по названию и описанию (SQL ILIKE) |
| `category_id` | UUID    | Фильтр по категории                      |
| `tag`         | string  | Фильтр по slug тега                      |
| `min_rating`  | float   | Минимальный средний рейтинг              |
| `is_published`| boolean | Фильтр по статусу публикации             |
| `limit`       | int     | Количество записей (по умолчанию 20)     |
| `offset`      | int     | Смещение для пагинации                   |

> Для full-text поиска с typo tolerance используйте `GET /search/items`.

### Основные эндпоинты

| Метод  | Путь          | Описание              | Доступ |
|--------|---------------|-----------------------|--------|
| GET    | `/items`      | Список объектов       | Public |
| GET    | `/items/{id}` | Получить объект по ID | Public |
| POST   | `/items`      | Создать объект        | Admin  |
| PATCH  | `/items/{id}` | Обновить объект       | Admin  |
| DELETE | `/items/{id}` | Удалить объект        | Admin  |

> `GET /items/{id}` инкрементирует `view_count` на 1 при каждом запросе.

**Ответ `GET /items/{id}`:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Sony WH-1000XM5",
  "short_description": "Флагманские наушники с ANC",
  "description": "...",
  "category_id": "uuid",
  "youtube_url": "https://youtube.com/watch?v=...",
  "marketplace_links": [
    { "name": "DNS", "url": "https://dns.ru/...", "price": "24990 ₽" }
  ],
  "is_published": true,
  "view_count": 1247,
  "characteristics": [
    { "id": "uuid", "group": "Звук", "name": "Частотный диапазон", "value": "4 Гц – 40 кГц" }
  ],
  "gallery": [
    { "id": "uuid", "image_url": "items/550e8400.jpg" }
  ],
  "tags": [
    { "id": "uuid", "name": "Наушники", "slug": "nausniki" }
  ],
  "created_at": "2026-06-01T12:00:00Z",
  "updated_at": "2026-06-20T10:30:00Z"
}
```

**Ответ `GET /items` (список):**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Sony WH-1000XM5",
      "short_description": "...",
      "category_id": "uuid",
      "youtube_url": null,
      "is_published": true,
      "view_count": 1247,
      "preview_image": "items/uuid.jpg",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "total": 145
}
```

### Теги объекта

| Метод  | Путь                        | Описание    | Доступ |
|--------|-----------------------------|-------------|--------|
| POST   | `/items/{id}/tags`          | Привязать тег | Admin |
| DELETE | `/items/{id}/tags/{tag_id}` | Отвязать тег  | Admin |

**Body `POST /items/{id}/tags`:** `{ "tag_id": "uuid" }`

### Характеристики объекта

| Метод  | Путь                                    | Описание                | Доступ |
|--------|-----------------------------------------|-------------------------|--------|
| POST   | `/items/{id}/characteristics`           | Добавить характеристику | Admin  |
| PATCH  | `/items/{id}/characteristics/{char_id}` | Обновить характеристику | Admin  |
| DELETE | `/items/{id}/characteristics/{char_id}` | Удалить характеристику  | Admin  |

**Body `POST`:** `{ "group": "string|null", "name": "string", "value": "string" }`

**Body `PATCH`:** все поля опциональны: `{ "group": "string|null", "name": "string|null", "value": "string|null" }`

### Галерея объекта

| Метод  | Путь                             | Описание             | Доступ |
|--------|----------------------------------|----------------------|--------|
| POST   | `/items/{id}/gallery`            | Добавить изображение | Admin  |
| DELETE | `/items/{id}/gallery/{image_id}` | Удалить изображение  | Admin  |

**Body `POST`:** `{ "image_url": "items/uuid.jpg" }` (MinIO-ключ после загрузки через `/upload`)

---

## Теги `/tags`

| Метод  | Путь         | Описание          | Доступ |
|--------|--------------|-------------------|--------|
| GET    | `/tags`      | Получить все теги | Public |
| POST   | `/tags`      | Создать тег       | Admin  |
| DELETE | `/tags/{id}` | Удалить тег       | Admin  |

---

## Комментарии `/items/{id}/comments`

| Метод  | Путь                                | Описание                     | Доступ              |
|--------|-------------------------------------|------------------------------|---------------------|
| GET    | `/items/{id}/comments`              | Получить комментарии объекта | Public              |
| POST   | `/items/{id}/comments`              | Добавить комментарий         | User                |
| PATCH  | `/items/{id}/comments/{comment_id}` | Редактировать комментарий    | User (свой)         |
| DELETE | `/items/{id}/comments/{comment_id}` | Удалить комментарий          | User (свой) / Admin |

---

## Рейтинг `/items/{id}/rating`

| Метод  | Путь                 | Описание                        | Доступ |
|--------|----------------------|---------------------------------|--------|
| GET    | `/items/{id}/rating` | Получить средний рейтинг объекта | Public |
| POST   | `/items/{id}/rating` | Поставить оценку (1–5)          | User   |
| PATCH  | `/items/{id}/rating` | Изменить свою оценку            | User   |
| DELETE | `/items/{id}/rating` | Убрать свою оценку              | User   |

**Ответ `GET /items/{id}/rating`:**
```json
{ "average": 4.3, "count": 12, "user_score": 5 }
```
`user_score` — оценка текущего пользователя (null если гость или не оценивал).

**Побочный эффект `POST /items/{id}/rating`:** запускает Celery-задачу `recalculate_item_rating` (очередь `default`, идемпотентна).

---

## Загрузка файлов `/upload`

| Метод | Путь      | Описание                               | Доступ |
|-------|-----------|----------------------------------------|--------|
| POST  | `/upload` | Загрузить изображение (multipart/form) | Admin  |

**Query params:** `section=items|categories|users` (обязательный)

**Ответ (201):**
```json
{ "key": "items/550e8400-e29b-41d4-a716-446655440000.jpg" }
```
`key` — MinIO-ключ. Используется в `gallery.image_url`, `category.image_url`, `user.avatar_url`.

**Побочный эффект:** запускает Celery-задачу `generate_thumbnail` (очередь `images`). Thumbnail сохраняется с ключом `items/thumb_<uuid>.jpg`. HTTP-ответ возвращается немедленно — thumbnail генерируется в фоне.

---

## Хранилище `/storage`

| Метод | Путь                      | Описание                          | Доступ |
|-------|---------------------------|-----------------------------------|--------|
| POST  | `/storage/presigned-urls` | Получить presigned URL для ключей | Public |

**Body:**
```json
{
  "keys": ["items/uuid.jpg", "blog/uuid.png"],
  "expires_in": 3600
}
```

**Ответ (200):**
```json
{
  "urls": {
    "items/uuid.jpg": "https://minio.example.com/coremarket/items/uuid.jpg?X-Amz-...",
    "blog/uuid.png": "https://minio.example.com/coremarket/blog/uuid.png?X-Amz-..."
  }
}
```

> Frontend кэширует presigned URLs в Redis (db 1) 45 минут через Next.js CacheHandler. MinIO выдаёт TTL 2 часа, что обеспечивает запас для пересборки кэша.

---

## Поиск `/search`

> Требует `SEARCH_ENABLED=true` и доступного Elasticsearch. При `SEARCH_ENABLED=false` или недоступности ES возвращает `503 Service Unavailable`.
>
> Для базовой фильтрации (без typo tolerance и relevance ranking) используйте `GET /items?search=query`.

### `GET /search/items`

Full-text поиск по каталогу с typo tolerance, relevance ranking и фильтрами.

**Query параметры:**

| Параметр      | Тип    | По умолчанию | Ограничения   | Описание                                              |
|---------------|--------|--------------|---------------|-------------------------------------------------------|
| `q`           | string | null         | —             | Поисковый запрос (RU+EN, typo tolerance)              |
| `category_id` | UUID   | null         | —             | Фильтр по категории                                   |
| `tag`         | string | null         | —             | Фильтр по slug тега                                   |
| `min_rating`  | float  | null         | 1 ≤ x ≤ 5    | Минимальный средний рейтинг                           |
| `sort_by`     | string | `relevance`  | см. ниже      | Сортировка результатов                                |
| `limit`       | int    | 20           | 1 ≤ x ≤ 100  | Количество результатов на страницу                    |
| `offset`      | int    | 0            | ≥ 0           | Смещение для пагинации                                |

**Допустимые значения `sort_by`:**

| Значение     | Описание                                                     |
|--------------|--------------------------------------------------------------|
| `relevance`  | По релевантности (BM25 + popularity boost) — по умолчанию   |
| `rating`     | По среднему рейтингу (убыв.)                                 |
| `views`      | По количеству просмотров (убыв.)                             |
| `newest`     | По дате создания (убыв.)                                     |
| `popularity` | По popularity score: `rating * 0.6 + log1p(views) * 0.4`    |

**Пример запроса:**
```
GET /api/v1/search/items?q=наушники+sony&category_id=uuid&sort_by=relevance&limit=20&offset=0
```

**Ответ (200):**
```json
{
  "hits": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Sony WH-1000XM5",
      "short_description": "Флагманские наушники с ANC",
      "category_id": "uuid",
      "tags": ["наушники", "sony", "anc"],
      "rating_avg": 4.7,
      "view_count": 1247,
      "is_published": true,
      "created_at": "2026-06-01T12:00:00Z",
      "updated_at": "2026-06-20T10:30:00Z",
      "preview_image_key": "items/550e8400.jpg",
      "score": 8.42
    }
  ],
  "total": 34,
  "took_ms": 12,
  "query": "наушники sony",
  "page": 1,
  "page_size": 20
}
```

**Поля ответа:**

| Поле               | Тип              | Описание                                                   |
|--------------------|------------------|------------------------------------------------------------|
| `hits`             | array            | Результаты поиска                                          |
| `hits[].score`     | float            | Релевантность документа (ES `_score` с popularity boost)   |
| `hits[].preview_image_key` | string\|null | MinIO-ключ превью (передать в `/storage/presigned-urls`) |
| `total`            | int              | Общее число совпадений (для пагинации)                     |
| `took_ms`          | int              | Время выполнения запроса в Elasticsearch (мс)              |
| `query`            | string\|null     | Нормализованный поисковый запрос                           |
| `page`             | int              | Номер текущей страницы (1-based)                           |
| `page_size`        | int              | Размер страницы                                            |

---

### `GET /search/suggestions`

Autocomplete — быстрые подсказки по введённому тексту (edge ngram, min 2 символа).

**Query параметры:**

| Параметр | Тип    | По умолчанию | Ограничения        | Описание             |
|----------|--------|--------------|--------------------|-----------------------|
| `q`      | string | (обязательный) | 1 ≤ длина ≤ 100  | Строка для автодополнения |
| `limit`  | int    | 8            | 1 ≤ x ≤ 20       | Максимум подсказок    |

**Пример запроса:**
```
GET /api/v1/search/suggestions?q=наушн&limit=5
```

**Ответ (200):**
```json
{
  "suggestions": [
    { "id": "uuid-1", "title": "Sony WH-1000XM5", "score": 9.1 },
    { "id": "uuid-2", "title": "Sony WF-1000XM4", "score": 8.7 },
    { "id": "uuid-3", "title": "Наушники Bose QC45", "score": 7.2 }
  ],
  "query": "наушн"
}
```

---

### `POST /search/reindex`

Полный пересчёт Elasticsearch индекса из PostgreSQL. Пересоздаёт маппинги и переиндексирует все товары.

**Доступ:** Admin (требует Bearer токен с ролью `admin`)

**Тело запроса:** не требуется

**Ответ (200):**
```json
{
  "indexed": 1247,
  "message": "Successfully reindexed 1247 items"
}
```

> Операция синхронная относительно HTTP-запроса — ответ возвращается после завершения переиндексации. Для больших каталогов используйте CLI: `python -m src.backend.scripts.reindex`.

---

## Homepage `/homepage`

| Метод | Путь        | Описание                              | Доступ |
|-------|-------------|---------------------------------------|--------|
| GET   | `/homepage` | Precomputed homepage data (cache-first) | Public |

Возвращает агрегированный snapshot данных для главной страницы. Primary path: Redis (<5 мс). Fallback: inline DB query.

**Ответ (200):**
```json
{
  "source": "cache",
  "computed_at": 1750892400.0,
  "featured_items": [...],
  "top_rated_items": [...],
  "categories": [...],
  "recent_posts": [...],
  "stats": {
    "total_items": 1247,
    "total_categories": 12,
    "total_posts": 48
  }
}
```

| Поле               | Описание                                                       |
|--------------------|----------------------------------------------------------------|
| `source`           | `"cache"` — из Redis, `"db_fallback"` — live DB query         |
| `computed_at`      | Unix timestamp последнего пересчёта snapshot                  |
| `featured_items`   | До 20 товаров, отсортированных по `view_count DESC`           |
| `top_rated_items`  | До 10 товаров по `avg_rating DESC` (минимум 1 оценка)         |
| `categories`       | Все категории с количеством опубликованных товаров             |
| `recent_posts`     | 6 последних опубликованных блог-постов                        |
| `stats`            | Агрегированные счётчики                                       |

> Snapshot обновляется Celery beat каждые 5 минут (задача `compute_homepage_snapshot`, очередь `homepage`). При cache miss автоматически запускает async rebuild.

---

## Блог `/blog`

### Посты

| Метод  | Путь                                    | Описание                      | Доступ |
|--------|-----------------------------------------|-------------------------------|--------|
| GET    | `/blog/posts`                           | Список постов                 | Public |
| GET    | `/blog/posts/{slug}`                    | Получить пост по slug         | Public |
| POST   | `/blog/posts`                           | Создать пост                  | Admin  |
| PATCH  | `/blog/posts/{slug}`                    | Обновить пост                 | Admin  |
| DELETE | `/blog/posts/{slug}`                    | Удалить пост                  | Admin  |
| POST   | `/blog/posts/{slug}/publish`            | Опубликовать пост             | Admin  |
| POST   | `/blog/posts/{slug}/unpublish`          | Снять с публикации            | Admin  |
| POST   | `/blog/posts/{slug}/archive`            | Архивировать пост             | Admin  |
| POST   | `/blog/posts/{slug}/cover`              | Загрузить обложку (multipart) | Admin  |
| POST   | `/blog/posts/{slug}/tags`               | Добавить тег к посту          | Admin  |
| DELETE | `/blog/posts/{slug}/tags/{tag_id}`      | Убрать тег с поста            | Admin  |
| POST   | `/blog/posts/{slug}/products`           | Привязать товар к посту       | Admin  |
| DELETE | `/blog/posts/{slug}/products/{link_id}` | Убрать товар с поста          | Admin  |

**Query params `GET /blog/posts`:**

| Параметр      | Тип    | Описание                                     |
|---------------|--------|----------------------------------------------|
| `search`      | string | Поиск по заголовку                           |
| `category_id` | UUID   | Фильтр по категории                          |
| `tag_slug`    | string | Фильтр по slug тега блога                   |
| `post_status` | string | Фильтр по статусу (draft/published/archived) |
| `limit`       | int    | Количество (по умолчанию 20)                 |
| `offset`      | int    | Смещение                                     |

**Body `POST /blog/posts`:** `{ "title": "string", "slug": "string", "short_description": "string|null" }`

**Body `POST /blog/posts/{slug}/products`:** `{ "product_id": "uuid", "display_order": 0 }`

### Теги блога

| Метод  | Путь                    | Описание           | Доступ |
|--------|-------------------------|--------------------|--------|
| GET    | `/blog/tags`            | Список тегов блога | Public |
| POST   | `/blog/tags`            | Создать тег        | Admin  |
| PATCH  | `/blog/tags/{tag_id}`   | Обновить тег       | Admin  |
| DELETE | `/blog/tags/{tag_id}`   | Удалить тег        | Admin  |

---

## Метрики `/metrics`

| Метод | Путь       | Описание                  | Доступ                |
|-------|------------|---------------------------|------------------------|
| GET   | `/metrics` | Prometheus scrape endpoint | Internal (Prometheus)  |

Возвращает метрики в формате Prometheus text exposition. Используется `prometheus` сервисом для scrape.

---

## Асинхронное поведение

Ряд HTTP-запросов запускает фоновые Celery-задачи. HTTP-ответ возвращается **немедленно**, задача выполняется асинхронно.

| Эндпоинт                        | Celery-задача                  | Очередь       | Описание                                     |
|---------------------------------|--------------------------------|---------------|----------------------------------------------|
| `POST /auth/register`           | `send_welcome_email`           | `emails`      | Приветственный email (3 retries, SMTP)       |
| `POST /items/{id}/rating`       | `recalculate_item_rating`      | `default`     | Пересчёт `avg_rating` в PostgreSQL           |
| `POST /upload`                  | `generate_thumbnail`           | `images`      | Генерация thumbnail 400×300 в MinIO          |
| `POST /items`                   | `index_item_task`              | `search_sync` | Индексация нового товара в Elasticsearch     |
| `PATCH /items/{id}`             | `index_item_task`              | `search_sync` | Обновление документа в Elasticsearch         |
| `DELETE /items/{id}`            | `delete_item_task`             | `search_sync` | Удаление документа из Elasticsearch          |
| Celery beat (каждые 5 мин)      | `compute_homepage_snapshot`    | `homepage`    | Пересчёт homepage snapshot → Redis           |
| Celery beat (02:00 UTC)         | `cleanup_expired_sessions`     | `default`     | Удаление soft-deleted комментариев (90+ дней)|

> Search sync задачи выполняются только при `SEARCH_ENABLED=true`. При `false` задачи завершаются немедленно с `{"skipped": true}`.

---

## Коды ошибок

### Стандартные коды

| Код  | Описание                                          |
|------|---------------------------------------------------|
| 400  | Некорректный запрос (BadRequestError)             |
| 401  | Не авторизован / невалидный / истёкший JWT        |
| 403  | Недостаточно прав (требуется admin)               |
| 404  | Объект не найден (NotFoundError)                  |
| 409  | Конфликт (ConflictError) — например, slug занят  |
| 422  | Ошибка валидации Pydantic                         |
| 429  | Превышен rate limit (slowapi)                     |
| 503  | Сервис недоступен (Search / Homepage)             |

**Формат ошибки (400/401/403/404/409):**
```json
{ "detail": "Human-readable error message" }
```

**Формат ошибки 422 (Pydantic validation):**
```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["body", "view_count"],
      "msg": "Input should be greater than or equal to 1",
      "input": 0,
      "ctx": { "ge": 1 }
    }
  ]
}
```

**Формат ошибки 503 (Search недоступен):**
```json
{ "detail": "Search service temporarily unavailable" }
```

```json
{ "detail": "Search service is disabled" }
```

### Типичные сценарии ошибок

```
# Попытка создать элемент с дублирующим slug
POST /blog/posts  { "slug": "existing-slug" }
→ 409 Conflict: { "detail": "Blog post with this slug already exists" }

# Запрос к несуществующему объекту
GET /items/00000000-0000-0000-0000-000000000000
→ 404 Not Found: { "detail": "Item not found" }

# Нет Bearer токена
PATCH /items/{id}
→ 401 Unauthorized: { "detail": "Not authenticated" }

# Пользователь без прав admin
PATCH /items/{id}  (User токен)
→ 403 Forbidden: { "detail": "Admin access required" }

# Rate limit превышен
POST /auth/login (6-й запрос за минуту)
→ 429 Too Many Requests: { "detail": "5 per 1 minute" }

# view_count = 0
PATCH /items/{id}  { "view_count": 0 }
→ 422 Unprocessable Entity
```

---

## Заметки о производительности

### Redis кэш

- **Presigned URLs:** frontend кэширует через Next.js CacheHandler (Redis db 1, TTL 45 мин). Повторные страницы не делают запрос к `/storage/presigned-urls`.
- **Homepage snapshot:** `GET /homepage` отвечает из Redis (<5 мс) при наличии snapshot. Snapshot обновляется каждые 5 минут.
- **ISR страницы:** `/catalog/[category]`, `/tags/[slug]`, `/blog/[slug]` — первый запрос кэшируется в Redis (db 1), последующие отдаются без обращения к API.

### `GET /items/{id}` и view_count

`view_count` инкрементируется при каждом `GET /items/{id}`. Страница item detail использует `force-dynamic` — кэширование на уровне Next.js для неё отключено, чтобы счётчик был точным.

### Elasticsearch vs SQL поиск

`GET /items?search=query` — SQL ILIKE, без typo tolerance, без relevance ranking. Рекомендуется только как fallback.
`GET /search/items?q=query` — Elasticsearch, с typo tolerance, popularity boost, RU+EN анализаторами. Используется как основной поиск при `SEARCH_ENABLED=true`.
