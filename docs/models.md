# Модели данных

## User (Пользователь)

Зарегистрированный пользователь системы.

| Поле            | Тип      | Описание                        |
| --------------- | -------- | ------------------------------- |
| id              | UUID     | Уникальный идентификатор        |
| username        | string   | Имя пользователя (уникальное)   |
| email           | string   | Email (уникальный)              |
| hashed_password | string   | Хэш пароля                      |
| role            | enum     | `admin` / `user`                |
| is_active       | boolean  | Активен ли аккаунт              |
| avatar_url      | string   | MinIO-ключ аватара (опционально) |
| created_at      | datetime | Дата регистрации                |
| updated_at      | datetime | Дата обновления                 |

---

## Category (Категория)

Группирует объекты по типу. Используется и для каталога товаров, и для блог-постов.

**Примеры:** Телефоны, Машины, Новости, Технологии

| Поле        | Тип      | Описание                 |
| ----------- | -------- | ------------------------ |
| id          | UUID     | Уникальный идентификатор |
| name        | string   | Название категории       |
| slug        | string   | URL-имя                  |
| description | text     | Описание категории       |
| image_url   | string   | MinIO-ключ изображения   |
| created_at  | datetime | Дата создания            |

---

## Item (Объект / Карточка)

Основная карточка контента.

| Поле              | Тип      | Описание                                                                 |
| ----------------- | -------- | ------------------------------------------------------------------------ |
| id                | UUID     | Уникальный идентификатор                                                 |
| category_id       | UUID     | ID категории                                                             |
| title             | string   | Название (`name` в БД, до 500 символов)                                 |
| short_description | string   | Краткое описание (до 1000 символов)                                     |
| description       | text     | Полное описание                                                          |
| youtube_url       | string   | Ссылка на YouTube-обзор (опционально)                                    |
| marketplace_links | JSONB    | Ссылки на маркетплейсы `[{name, url, price?}]`                          |
| is_published      | boolean  | Опубликовано ли                                                          |
| view_count        | integer  | Счётчик просмотров — auto-increment + ручное задание через admin         |
| avg_rating        | float    | Кэшированный средний рейтинг (обновляется Celery-задачей, может быть NULL) |
| created_at        | datetime | Дата создания                                                            |
| updated_at        | datetime | Дата обновления                                                          |

### view_count

- Автоматически инкрементируется при каждом `GET /items/{id}` через `increment_view_count()`.
- Доступен для ручного задания администратором (`set_view_count(count)`): **обязательно `>= 1`**, тип integer (не boolean).
- Используется в homepage snapshot (top 20 по просмотрам), в ES-индексе как popularity signal.

### avg_rating (cached)

- Опциональный кэш-столбец: заполняется Celery-задачей `recalculate_item_rating` после каждого нового голоса.
- Может быть `NULL`, если ещё ни одного голоса или Celery-задача не выполнилась.
- Используется в homepage snapshot (top 10 по рейтингу) и в ES-индексе для сортировки.
- Если столбец отсутствует в БД — задача завершается без ошибки (safe no-op).

### Производные поля (не в БД)

| Поле              | Источник                                                   | Описание |
| ----------------- | ---------------------------------------------------------- | -------- |
| `preview_image`   | первый элемент `gallery` по `id ASC`                       | MinIO-ключ превью; вычисляется `GalleryRepository.get_preview_keys()` |
| `tags`            | join `item_tags` → `tags`                                  | список тегов объекта |

### Elasticsearch — поисковая интеграция

При создании, обновлении и удалении объекта Celery-задача `index_item_task` синхронизирует запись в ES-индекс `{prefix}_items`. Документ включает все текстовые поля, рейтинг и view_count для relevance scoring. Подробнее — в разделе [Elasticsearch Item Document](#elasticsearch-item-document).

---

## MarketplaceLink (Ссылка на маркетплейс)

Хранится как JSONB-массив в `Item.marketplace_links`.

| Поле  | Тип    | Описание                             |
| ----- | ------ | ------------------------------------ |
| name  | string | Название маркетплейса (DNS, Amazon…) |
| url   | string | Ссылка на страницу товара            |
| price | string | Цена (опционально, например "от 99 990 ₽") |

---

## Characteristic (Характеристика)

Характеристики объекта (ключ-значение) с поддержкой группировки.

Группировка нужна для визуального разделения спецификаций по разделам:
например "Габариты и вес", "Функции", "Класс эффективности".
Характеристики без группы отображаются на верхнем уровне.

| Поле    | Тип    | Описание                                                      |
| ------- | ------ | ------------------------------------------------------------- |
| id      | UUID   | Уникальный идентификатор                                      |
| item_id | UUID   | ID объекта                                                    |
| group   | string | Название группы (опционально). Примеры: "Габариты и вес", "Функции" |
| name    | string | Название характеристики. Примеры: "Вес (кг)", "Тип загрузки" |
| value   | string | Значение. Примеры: "64", "Фронтальная", "52/70 дБ"           |

> Характеристики индексируются в ES как `nested` objects, что позволяет фильтровать по паре `name + value` без cross-field ложных срабатываний.

---

## Gallery (Галерея)

Дополнительные изображения объекта. Хранятся как MinIO-ключи.

| Поле      | Тип    | Описание                                       |
| --------- | ------ | ---------------------------------------------- |
| id        | UUID   | Уникальный идентификатор                       |
| item_id   | UUID   | ID объекта                                     |
| image_url | string | MinIO-ключ оригинала (напр. `items/uuid.jpg`)  |

### Thumbnail Generation (async)

После загрузки изображения Celery-задача `generate_thumbnail` генерирует thumbnail:

- **Размер:** 400×300 px (Pillow `LANCZOS`, `.thumbnail()`)
- **Формат:** JPEG, quality=85, optimize=True
- **Ключ thumbnail:** `<директория>/thumb_<uuid>.jpg` — рядом с оригиналом в MinIO
  - Пример: оригинал `items/abc123.jpg` → thumbnail `items/thumb_abc123.jpg`
- **Не хранится в БД** — thumbnail-ключ возвращается как результат задачи `{"thumb_key": "..."}`, но обратно в `gallery.image_url` не записывается
- **Retries:** до 3 раз с экспоненциальным backoff (30s, 60s, 120s)

---

## Tag (Тег)

Метка для объектов каталога. Один объект может иметь несколько тегов (M2M).

| Поле    | Тип    | Описание                 |
| ------- | ------ | ------------------------ |
| id      | UUID   | Уникальный идентификатор |
| name    | string | Название тега            |
| slug    | string | URL-имя (уникальное)     |

### Связь Item ↔ Tag

Таблица `item_tags` (many-to-many):

| Поле    | Тип  | Описание   |
| ------- | ---- | ---------- |
| item_id | UUID | ID объекта |
| tag_id  | UUID | ID тега    |

> `ondelete='CASCADE'` на обоих внешних ключах.

---

## Comment (Комментарий)

Комментарий пользователя к объекту.

| Поле       | Тип      | Описание                        |
| ---------- | -------- | ------------------------------- |
| id         | UUID     | Уникальный идентификатор        |
| item_id    | UUID     | ID объекта                      |
| user_id    | UUID     | ID пользователя                 |
| parent_id  | UUID     | ID родительского комментария (для вложенности, опционально) |
| text       | text     | Текст комментария (`body` в БД) |
| is_deleted | boolean  | Мягкое удаление                 |
| created_at | datetime | Дата создания                   |
| updated_at | datetime | Дата обновления                 |

> Мягко удалённые комментарии (`is_deleted=TRUE`) физически удаляются Celery-задачей `cleanup_expired_sessions` через 90 дней.

---

## Rating (Оценка товара)

Оценка объекта от пользователя. Один пользователь — одна оценка на объект.

| Поле       | Тип      | Описание                        |
| ---------- | -------- | ------------------------------- |
| id         | UUID     | Уникальный идентификатор        |
| item_id    | UUID     | ID объекта                      |
| user_id    | UUID     | ID пользователя                 |
| score      | integer  | Оценка от 1 до 5                |
| created_at | datetime | Дата оценки                     |
| updated_at | datetime | Дата обновления                 |

> Уникальность: `(item_id, user_id)` (`uq_rating_item_user`) — один голос на объект.

### Async Rating Recalculation

После каждого нового или обновлённого голоса:

1. Presentation layer ставит задачу `recalculate_item_rating` в очередь `ratings`.
2. Celery-воркер выполняет `AVG(score)` + `COUNT(*)` из таблицы `ratings`.
3. Результат (`avg`, `total`) пишется в `items.avg_rating` через `UPDATE items SET avg_rating = :avg WHERE id = :iid`.
4. Если столбец `avg_rating` отсутствует — `UPDATE` тихо откатывается, задача завершается успешно.
5. **Retries:** до 3 раз с backoff 5s, 10s, 20s.

> "On-demand" расчёт (на уровне репозитория) через `AVG(score)` по-прежнему доступен и используется при `GET /items/{id}` — кэш-столбец служит дополнительным источником для homepage snapshot и поиска.

---

## BlogPost (Блог-пост)

Статья блога с поддержкой markdown, SEO-полей и ссылок на товары каталога.

| Поле              | Тип      | Описание                                                  |
| ----------------- | -------- | --------------------------------------------------------- |
| id                | UUID     | Уникальный идентификатор                                  |
| title             | string   | Заголовок                                                 |
| slug              | string   | URL-имя (уникальное, индекс)                              |
| short_description | string   | Краткое описание (опционально)                            |
| content           | text     | Markdown-контент (опционально)                            |
| cover_image_url   | string   | MinIO-ключ обложки (опционально)                          |
| category_id       | UUID     | ID категории из таблицы `categories` (опционально)        |
| status            | string   | `draft` / `published` / `archived`                        |
| seo_title         | string   | SEO заголовок (опционально)                               |
| seo_description   | string   | SEO описание (опционально)                                |
| created_at        | datetime | Дата создания                                             |
| updated_at        | datetime | Дата обновления                                           |

> Таблица `blog_categories` удалена. Посты используют каталожные `Category` напрямую (`category_id` → `categories.id`).

---

## BlogTag (Тег блога)

Тег для блог-постов (отдельная сущность от `Tag` каталога).

| Поле | Тип    | Описание                    |
| ---- | ------ | --------------------------- |
| id   | UUID   | Уникальный идентификатор    |
| name | string | Название                    |
| slug | string | URL-имя (уникальное)        |

### Связь BlogPost ↔ BlogTag

Таблица `blog_post_tags` (many-to-many):

| Поле         | Тип  | Описание       |
| ------------ | ---- | -------------- |
| blog_post_id | UUID | ID блог-поста  |
| blog_tag_id  | UUID | ID тега блога  |

---

## BlogProductLink (Ссылка поста на товар)

Привязка блог-поста к товарам каталога (для блока "Товары из статьи").

| Поле          | Тип     | Описание                        |
| ------------- | ------- | ------------------------------- |
| id            | UUID    | Уникальный идентификатор        |
| blog_post_id  | UUID    | ID блог-поста                   |
| product_id    | UUID    | ID товара (`items.id`)          |
| display_order | integer | Порядок отображения (default 0) |

---

## Elasticsearch Item Document

Индекс: `{ELASTICSEARCH_INDEX_PREFIX}_items` (по умолчанию `coremarket_items`).  
Синхронизация: событийная (Celery `index_item_task` после create/update/delete) + bulk reindex через CLI.

### Поля документа

| Поле               | ES-тип    | Описание                                                   |
| ------------------ | --------- | ---------------------------------------------------------- |
| id                 | keyword   | UUID объекта                                               |
| title              | text      | Название; multi-field: `keyword`, `autocomplete`           |
| short_description  | text      | Краткое описание                                           |
| description        | text      | Полное описание                                            |
| category_id        | keyword   | UUID категории                                             |
| category_name      | keyword   | Название категории; sub-field `.text` для полнотекстового  |
| tags               | keyword[] | Слаги тегов; sub-field `.text`                             |
| tag_names          | text      | Имена тегов (пробел-разделённая строка)                    |
| rating_avg         | float     | Средний рейтинг (из ratings при индексации)                |
| view_count         | integer   | Счётчик просмотров (из items при индексации)               |
| is_published       | boolean   | Флаг публикации                                            |
| created_at         | date      | ISO-дата создания                                          |
| updated_at         | date      | ISO-дата обновления                                        |
| characteristics    | nested    | Список `{name, value, group}` — вложенный объект           |
| popularity_score   | float     | Денормализованный popularity signal (см. ниже)             |
| preview_image_key  | keyword   | MinIO-ключ превью (not indexed — только для _source)       |
| marketplace_links  | object    | JSONB ссылок (disabled — не индексируется)                 |

### Analyzers

| Analyzer              | Описание                                                            |
| --------------------- | ------------------------------------------------------------------- |
| `multilingual`        | standard tokenizer + lowercase + Russian/English stop words + stemming |
| `autocomplete_index`  | standard tokenizer + lowercase + edge_ngram (min=2, max=20)         |
| `autocomplete_search` | standard tokenizer + lowercase (без ngram при поиске)               |

> Поле `title` использует `multilingual` для основного поиска и `autocomplete_index` / `autocomplete_search` для prefix-completion через `title.autocomplete`.

### Field Boost при поиске (multi_match)

| Поле                   | Boost |
| ---------------------- | ----- |
| `title`                | ^4    |
| `title.autocomplete`   | ^2    |
| `short_description`    | ^2    |
| `tags.text`            | ^1.5  |
| `tag_names`            | ^1.5  |
| `description`          | ^1    |
| `category_name.text`   | ^1    |
| `characteristics.name` | ^1    |
| `characteristics.value`| ^1    |

### Popularity Score

```
popularity_score = rating_avg × 0.6 + log1p(view_count) × 0.4
```

Используется как:
- поле `popularity_score` в документе (pre-computed при индексации)
- дополнительный function_score при текстовом поиске: `rating_avg × sqrt × 0.15` + `log1p(view_count) × 0.001`

### Sort Options

| `sort_by`   | ES-сортировка                                    |
| ----------- | ------------------------------------------------ |
| `relevance` | `_score DESC`, `popularity_score DESC`           |
| `rating`    | `rating_avg DESC`, `view_count DESC`             |
| `views`     | `view_count DESC`                                |
| `newest`    | `created_at DESC`                                |
| _(default)_ | `popularity_score DESC`                          |

---

## Background Processing Flows

### Image Processing Flow

```
POST /upload  →  MinIO (оригинал сохранён)
                   └─► Celery queue: images
                         └─► generate_thumbnail(key, width=400, height=300)
                               ├─ download original from MinIO
                               ├─ Pillow resize (LANCZOS) + JPEG encode (q=85)
                               └─ upload thumb_<uuid>.jpg to MinIO
                                    (рядом с оригиналом, ключ возвращается в result)
```

- **Retries:** 3, exponential backoff: 30s → 60s → 120s
- Thumbnail-ключ не записывается обратно в `gallery.image_url` автоматически

### Search Sync Flow

```
POST/PUT/DELETE /items/{id}  →  use case
                                  └─► Celery queue: search
                                        ├─► index_item_task(item_id)
                                        │     ├─ fetch item + ratings + tags + gallery
                                        │     ├─ build ES document
                                        │     └─ es.index(index, id, doc)
                                        └─► delete_item_task(item_id)  [при удалении]
                                              └─ es.delete(index, id)

POST /search/reindex  →  bulk_reindex()  [batch=100, для массовой переиндексации]
```

- Если `SEARCH_ENABLED=False` — задача пропускается (`{"skipped": True}`)
- **Retries:** 3, backoff: 10s → 20s → 40s

### Rating Aggregation Flow

```
POST/PUT /items/{id}/ratings  →  use case  →  DB INSERT/UPDATE
                                               └─► Celery queue: ratings
                                                     └─► recalculate_item_rating(item_id)
                                                           ├─ SELECT AVG(score), COUNT(*) FROM ratings
                                                           └─ UPDATE items SET avg_rating = :avg
                                                                (safe no-op если столбец отсутствует)
```

- **Retries:** 3, backoff: 5s → 10s → 20s

### Comment Cleanup Flow

```
Celery Beat (периодически)  →  cleanup_expired_sessions
                                  └─ DELETE FROM comments
                                       WHERE is_deleted = TRUE
                                       AND updated_at < NOW() - INTERVAL '90 days'
```

---

## Redis / Cache

### Homepage Snapshot

- **Ключ:** `homepage:snapshot` (настраивается через `HOMEPAGE_SNAPSHOT_KEY`)
- **TTL:** 600 секунд (настраивается через `HOMEPAGE_SNAPSHOT_TTL`)
- **Обновляется:** Celery Beat каждые 5 минут через задачу `compute_homepage_snapshot` (queue: `homepage`)
- **Содержимое:**

| Поле              | Описание                                       |
| ----------------- | ---------------------------------------------- |
| `computed_at`     | Unix timestamp момента вычисления              |
| `featured_items`  | top 20 опубликованных объектов по `view_count` |
| `top_rated_items` | top 10 объектов по `avg_rating DESC` (где `avg_rating IS NOT NULL`) |
| `categories`      | все категории + `item_count` опубликованных товаров |
| `recent_posts`    | 6 последних опубликованных блог-постов         |
| `stats`           | `{total_items, total_categories, total_posts}` |

- **Fallback:** если Redis недоступен — API-эндпоинт `/api/v1/homepage` выполняет inline DB-запрос.
- **Observability:** при успешном обновлении Prometheus-gauge `homepage_snapshot_age_seconds` сбрасывается в 0.

### Presigned URL Cache

Presigned URL для MinIO (`POST /storage/presigned-urls`) кэшируются на frontend-стороне — TTL 45 минут (меньше срока действия URL).

---

## Validation Rules

### Item

| Поле              | Правило                                                |
| ----------------- | ------------------------------------------------------ |
| `title`           | string, не пустой; `Name` value object (domain layer)  |
| `short_description` | string, не пустой                                    |
| `view_count` (set) | integer >= 1, не boolean; проверяется в `set_view_count()` |
| `view_count` (auto) | начинается с 0, инкремент без ограничений снизу      |
| `marketplace_links` | список `MarketplaceLink` value objects               |

### Rating

| Поле    | Правило                |
| ------- | ---------------------- |
| `score` | integer 1 ≤ score ≤ 5 |

### Comment

| Поле       | Правило                          |
| ---------- | -------------------------------- |
| `text`     | непустой текст                   |
| `is_deleted` | `FALSE` по умолчанию, soft-delete через API |

### Gallery / Image Upload

| Аспект          | Правило                                      |
| --------------- | -------------------------------------------- |
| Хранение        | только MinIO-ключ, не полный URL             |
| Thumbnail       | генерируется асинхронно Celery, не блокирует upload |
| Формат thumbnail | JPEG, 400×300, quality=85                  |

### Elasticsearch

| Аспект         | Правило                                              |
| -------------- | ---------------------------------------------------- |
| Индексация     | только при `is_published` или явном admin-reindex    |
| `SEARCH_ENABLED` | `False` → все sync-задачи пропускаются             |
| Autocomplete   | `min_gram=2`, `max_gram=20` (edge_ngram)             |

---

## Relationships

```
Category (1) ──────────────── (N) Item
                                    │
                    ┌───────────────┼──────────────────┐
                    │               │                  │
              (N) Characteristic  (N) Gallery    (M2M) Tag
                                    │
                              (N) Rating  (per user, unique)
                              (N) Comment (threaded, soft-delete)

Category (1) ──── (N) BlogPost
BlogPost  (M2M) ── BlogTag
BlogPost  (1) ──── (N) BlogProductLink ──── (N) Item
```

> Все внешние ключи Item → `ondelete='CASCADE'`: удаление объекта каскадно удаляет характеристики, галерею, рейтинги, комментарии, теги (записи в `item_tags`) и ES-документ (через Celery `delete_item_task`).
