# Celery — асинхронные задачи

## Обзор

Асинхронная инфраструктура CoreMarket построена на **Celery + Redis**. Тяжёлые операции (email, обработка изображений, пересчёт рейтингов, ES-синхронизация, homepage precompute) выполняются в фоне — HTTP-запрос не ждёт их завершения.

```
FastAPI  ──.delay()──▶  Redis db 0 (broker)  ──▶  Celery Worker  ──▶  Redis db 0 (results)
                                                         │
                                                    Flower UI          Prometheus metrics
                                                http://localhost:5555    /metrics
```

---

## Архитектура очередей

Celery использует **5 изолированных очередей**. Каждая очередь имеет независимый приоритет и может быть направлена на отдельный worker с нужной конкурентностью.

```
Redis broker
  ├── default      ← lightweight ops (rating recalc, cleanup)
  ├── emails       ← transactional email (изолирован от IO-тяжёлых задач)
  ├── images       ← thumbnail generation (CPU + MinIO IO)
  ├── search_sync  ← Elasticsearch index/delete
  └── homepage     ← homepage snapshot precompute (scheduled, low priority)
```

**Зачем изоляция:** крупный backlog thumbnail-задач не блокирует доставку email. Задача search_sync не конкурирует с homepage scheduler. Каждая очередь масштабируется независимо через `-Q` флаг.

---

## Сервисы

| Сервис          | Образ           | Порт   | Назначение                                              |
|-----------------|-----------------|--------|---------------------------------------------------------|
| `redis`         | `redis:7-alpine`| —      | Broker (db 0) + Result backend (db 0)                   |
| `celery_worker` | `./backend`     | —      | Worker: слушает все 5 очередей одновременно             |
| `celery_beat`   | `./backend`     | —      | Beat: запускает периодические задачи по расписанию      |
| `flower`        | `./backend`     | `5555` | Мониторинг задач, воркеров, очередей                    |

Все сервисы в сети `coremarket`. Redis данные хранятся в volume `redis_data`.

---

## Конфигурация

### ENV переменные

| Переменная               | По умолчанию          | Описание                                    |
|--------------------------|-----------------------|---------------------------------------------|
| `REDIS_URL`              | `redis://redis:6379/0`| Broker и result backend (db 0)              |
| `CELERY_WORKER_CONCURRENCY` | `2`              | Число процессов воркера                     |
| `CELERY_TASK_ALWAYS_EAGER`  | `False`          | `True` → задачи синхронны (только для тестов)|

### `celery_app.py` — ключевые настройки

```python
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,          # результаты хранятся 1 час
    task_acks_late=True,          # задача удаляется из очереди ПОСЛЕ выполнения
    worker_prefetch_multiplier=1, # FIFO per queue, предотвращает starvation
    task_track_started=True,      # Flower видит STARTED статус
)
```

### Маршрутизация задач (`task_routes`)

| Задача (name)                              | Очередь       |
|--------------------------------------------|---------------|
| `coremarket.tasks.send_welcome_email`      | `emails`      |
| `coremarket.tasks.generate_thumbnail`      | `images`      |
| `coremarket.tasks.index_item`              | `search_sync` |
| `coremarket.tasks.delete_item_from_index`  | `search_sync` |
| `coremarket.tasks.recalculate_item_rating` | `default`     |
| `coremarket.tasks.cleanup_expired_sessions`| `default`     |
| `coremarket.tasks.compute_homepage_snapshot` | `homepage`  |

---

## Beat — периодические задачи

Beat запускается в отдельном контейнере `celery_beat`. Никогда не запускать несколько beat-экземпляров — это приведёт к дублированию задач.

```python
beat_schedule={
    "cleanup-expired-sessions-daily": {
        "task": "coremarket.tasks.cleanup_expired_sessions",
        "schedule": crontab(hour=2, minute=0),  # 02:00 UTC ежедневно
    },
    "homepage-snapshot-every-5m": {
        "task": "coremarket.tasks.compute_homepage_snapshot",
        "schedule": crontab(minute="*/5"),       # каждые 5 минут
    },
}
```

---

## Задачи

### `send_welcome_email` — приветственный email

**Файл:** `backend/src/backend/application/tasks/notifications.py`

```python
send_welcome_email.delay(user_id: str)
```

**Когда запускается:** `POST /api/v1/auth/register` — сразу после создания пользователя.

**Что делает:**
1. Берёт `email` и `username` из PostgreSQL по `user_id`
2. Если пользователь не найден — завершается со статусом `skipped`
3. Отправляет email через SMTP (если настроен `SMTP_HOST`) или логирует пропуск

**SMTP:** задача подхватывает `SMTP_HOST` / `SMTP_PORT` / `SMTP_FROM` из ENV автоматически.

**Retries:** 3 попытки, exponential backoff (60с → 120с → 240с).

**Очередь:** `emails`

---

### `recalculate_item_rating` — пересчёт рейтинга

**Файл:** `backend/src/backend/application/tasks/ratings.py`

```python
recalculate_item_rating.delay(item_id: str)
```

**Когда запускается:** `POST /api/v1/items/{id}/rating` — после создания оценки.

**Что делает:**
1. Считает `AVG(score)` и `COUNT(*)` из таблицы `ratings` для `item_id`
2. Обновляет `items.avg_rating`
3. Логирует результат с `avg_score` и `count`

Задача **идемпотентна** — повторный запуск безопасен.

**Retries:** 3 попытки, backoff (5с → 10с → 20с).

**Очередь:** `default`

---

### `generate_thumbnail` — генерация миниатюры

**Файл:** `backend/src/backend/application/tasks/images.py`

```python
generate_thumbnail.delay(key: str, width: int = 400, height: int = 300)
```

**Когда запускается:** `POST /api/v1/upload` — после загрузки любого изображения.

**Что делает:**
1. Скачивает оригинал из MinIO по `key`
2. Открывает через Pillow, конвертирует в RGB
3. Resize до `(width, height)` с сохранением пропорций (`Image.LANCZOS`)
4. Сжимает в JPEG (quality=85)
5. Загружает в MinIO с ключом `<section>/thumb_<uuid>.jpg`

**Пример:**
```
items/d0c7b30a-7364-4a5f-98e9-59c3409041d0.jpg
       ↓ (Pillow resize 400×300)
items/thumb_d0c7b30a-7364-4a5f-98e9-59c3409041d0.jpg
```

**Retries:** 3 попытки, backoff (30с → 60с → 120с).

**Очередь:** `images`

---

### `index_item_task` — индексация товара в Elasticsearch

**Файл:** `backend/src/backend/application/tasks/search_sync.py`

```python
index_item_task.delay(item_id: str)   # name: "coremarket.tasks.index_item"
```

**Когда запускается:** `POST /items` и `PATCH /items/{id}` — через helper `_dispatch_index()` в роутере.

**Что делает:**
1. Проверяет `SEARCH_ENABLED` — при `False` возвращает `{"skipped": True}`
2. Загружает актуальные данные товара из PostgreSQL
3. Строит ES-документ через `build_item_document()`
4. Выполняет `es.index()` в индекс `{prefix}_items`

**Retries:** 3 попытки, backoff (10с → 20с → 40с).

**Очередь:** `search_sync`

---

### `delete_item_task` — удаление товара из Elasticsearch

**Файл:** `backend/src/backend/application/tasks/search_sync.py`

```python
delete_item_task.delay(item_id: str)  # name: "coremarket.tasks.delete_item_from_index"
```

**Когда запускается:** `DELETE /items/{id}` — через helper `_dispatch_delete()` в роутере.

**Что делает:**
1. Проверяет `SEARCH_ENABLED` — при `False` возвращает `{"skipped": True}`
2. Выполняет `es.delete()` из индекса по `item_id`
3. Если документ не найден (404 от ES) — завершается без ошибки (idempotent)

**Retries:** 3 попытки, backoff (10с → 20с → 40с).

**Очередь:** `search_sync`

---

### `compute_homepage_snapshot` — precompute главной страницы

**Файл:** `backend/src/backend/application/tasks/homepage.py`

```python
# Вызывается автоматически через beat schedule
compute_homepage_snapshot.apply_async(countdown=0)  # или при cache miss
```

**Когда запускается:** beat каждые 5 минут + при cache miss в `GET /homepage`.

**Что делает:**
1. Делает 5 SQL-запросов к PostgreSQL:
   - Top 20 items by `view_count DESC` (featured)
   - Top 10 items by `avg_rating DESC` (top_rated, нужна минимум 1 оценка)
   - Все категории с количеством опубликованных товаров
   - 6 последних published blog posts
   - Агрегированные счётчики (items, categories, posts)
2. Сериализует результат в JSON
3. Сохраняет в Redis с ключом `homepage:snapshot`, TTL 10 минут
4. Обновляет Prometheus gauge `homepage_snapshot_age_seconds → 0`

**Fallback:** если Redis недоступен — логирует предупреждение, API endpoint делает inline DB query.

**Retries:** 2 попытки, backoff (30с → 60с).

**Очередь:** `homepage`

---

### `cleanup_expired_sessions` — плановая очистка

**Файл:** `backend/src/backend/application/tasks/cleanup.py`

```python
cleanup_expired_sessions()  # вызывается автоматически через beat
```

**Расписание:** каждый день в **02:00 UTC**.

**Что делает:** удаляет soft-deleted комментарии (`is_deleted = TRUE`) старше 90 дней.

**Retries:** 2 попытки с задержкой 5 минут.

**Очередь:** `default`

---

## Интеграция с FastAPI

Вызовы задач — fire-and-forget: HTTP-ответ возвращается клиенту немедленно, задача выполняется в фоне.

```python
# auth/router.py — после регистрации
from src.backend.application.tasks.notifications import send_welcome_email
send_welcome_email.delay(str(result.user_id))

# rating/router.py — после создания рейтинга
from src.backend.application.tasks.ratings import recalculate_item_rating
recalculate_item_rating.delay(str(item_id))

# upload/router.py — после загрузки изображения
from src.backend.application.tasks.images import generate_thumbnail
generate_thumbnail.delay(key)

# item/router.py — после create/update (через helper)
def _dispatch_index(item_id: str) -> None:
    if get_settings().SEARCH_ENABLED:
        index_item_task.delay(item_id)

# item/router.py — после delete (через helper)
def _dispatch_delete(item_id: str) -> None:
    if get_settings().SEARCH_ENABLED:
        delete_item_task.delay(item_id)
```

Импорт задачи внутри функции (не на уровне модуля) предотвращает циклические импорты между FastAPI и Celery.

---

## Flower — мониторинг

**URL:** http://localhost:5555

### Что показывает

| Вкладка   | Данные                                                                 |
|-----------|------------------------------------------------------------------------|
| Dashboard | Общее число задач, активные воркеры, скорость обработки                |
| Workers   | Онлайн-воркеры, concurrency, registered tasks, очереди                 |
| Tasks     | История выполненных задач: статус, время, аргументы, результат         |
| Broker    | Очереди Redis, число сообщений в каждой очереди                        |

### API Flower

```bash
# Список задач (последние N)
GET http://localhost:5555/api/tasks

# Список воркеров (с принудительным refresh)
GET http://localhost:5555/api/workers?refresh=1

# Детали конкретной задачи
GET http://localhost:5555/api/task/info/{task_id}

# Список очередей
GET http://localhost:5555/api/queues/length
```

### Диагностика упавших задач

1. Открыть Flower → вкладка Tasks → фильтр по статусу `FAILURE`
2. Нажать на задачу → вкладка Result → смотреть traceback
3. Проверить логи в Grafana Loki: `{compose_service="celery_worker"} | json | msg="task_failed"`
4. Для ручного retry через Flower API:
   ```bash
   POST http://localhost:5555/api/task/retry/{task_id}
   ```

---

## Celery + Observability

### Prometheus-метрики

Celery signals (`task_prerun`, `task_postrun`, `task_failure`, `task_retry`) подключены в `celery_app.py`. Метрики обновляются автоматически для каждой задачи:

| Метрика                                       | Тип       | Labels                              |
|-----------------------------------------------|-----------|-------------------------------------|
| `coremarket_celery_tasks_total`               | Counter   | `task_name`, `queue`, `status`      |
| `coremarket_celery_task_duration_seconds`     | Histogram | `task_name`, `queue`                |
| `coremarket_celery_tasks_active`              | Gauge     | `queue`                             |
| `coremarket_homepage_requests_total`          | Counter   | `source` (cache_hit/cache_miss/fallback) |
| `coremarket_homepage_snapshot_age_seconds`    | Gauge     | —                                   |

### Grafana дашборд `celery-metrics.json`

Показывает:
- Task throughput (tasks/min) по очередям
- Duration p50/p95 по каждой задаче
- Failure rate и retry count
- Active tasks gauge по очередям
- Homepage snapshot freshness (age_seconds)

### Логирование задач

Воркер использует тот же JSON-форматтер, что и FastAPI (`logging_setup.py`). Настройка через сигнал `worker_process_init`.

Каждая задача логирует начало, завершение и ошибки:

```json
{ "ts": "2026-06-26T10:00:00Z", "level": "INFO",
  "logger": "coremarket.tasks.notifications",
  "msg": "task_started", "task_id": "uuid", "task_name": "coremarket.tasks.send_welcome_email",
  "user_id": "uuid" }

{ "ts": "2026-06-26T10:00:01Z", "level": "INFO",
  "logger": "coremarket.tasks.notifications",
  "msg": "task_completed", "task_id": "uuid", "status": "success", "duration_ms": 312 }

{ "ts": "2026-06-26T10:00:01Z", "level": "ERROR",
  "logger": "coremarket.tasks.search_sync",
  "msg": "task_failed", "task_id": "uuid", "item_id": "uuid", "retry": 1, "duration_ms": 5042 }
```

### LogQL-запросы в Grafana

```logql
# Все failed задачи
{compose_service="celery_worker"} | json | msg="task_failed"

# Задачи по конкретному имени
{compose_service="celery_worker"} | json | task_name="coremarket.tasks.generate_thumbnail"

# Медленные задачи (>5 сек)
{compose_service="celery_worker"} | json | msg="task_completed" | duration_ms > 5000

# Homepage snapshot refreshes
{compose_service="celery_worker"} | json | task_name="coremarket.tasks.compute_homepage_snapshot" | msg="task_completed"
```

---

## Критически важные флаги

Без этих параметров инфраструктура работает некорректно:

| Параметр                       | Где                    | Последствие без него                                              |
|--------------------------------|------------------------|-------------------------------------------------------------------|
| `-E` (task events)             | `celery_worker` command | Flower не получает события — задачи не отображаются              |
| `FLOWER_UNAUTHENTICATED_API=1` | `flower` environment   | `/api/tasks` и `/api/workers` возвращают 403                     |
| `--persistent=True --db=/flower.db` | `flower` command | Воркер пропадает из `/api/workers` после рестарта Flower         |
| `healthcheck: disable`         | все Celery-сервисы     | Статус `unhealthy` (Dockerfile проверяет FastAPI `/health`)      |

---

## Тестирование

Задачи тестируются с `CELERY_TASK_ALWAYS_EAGER=True` — в этом режиме `.delay()` выполняется синхронно без брокера.

```python
@pytest.fixture(autouse=True)
def celery_eager():
    from src.backend.celery_app import celery_app
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = False
    celery_app.conf.task_eager_propagates = False
```

**Файлы тестов:**
- `backend/tests/tasks/test_notifications.py` — unit tests, mock `asyncio.run`, проверка skip/send/log
- `backend/tests/tasks/test_images.py` — unit + async integration, mock MinIO + Pillow resize

---

## Структура файлов

```
backend/src/backend/
├── celery_app.py                        ← Celery app, 5 очередей, task_routes, beat_schedule,
│                                          worker_process_init logging, Prometheus signals
└── application/
    └── tasks/
        ├── __init__.py
        ├── notifications.py             ← send_welcome_email (queue: emails)
        ├── ratings.py                   ← recalculate_item_rating (queue: default)
        ├── images.py                    ← generate_thumbnail (queue: images)
        ├── cleanup.py                   ← cleanup_expired_sessions (queue: default, beat)
        ├── search_sync.py               ← index_item_task, delete_item_task (queue: search_sync)
        └── homepage.py                  ← compute_homepage_snapshot (queue: homepage, beat)

backend/tests/tasks/
├── __init__.py
├── test_notifications.py
└── test_images.py
```

---

## Добавление новой задачи

1. Создать файл в `application/tasks/<domain>.py`
2. Декорировать функцию:
   ```python
   @celery_app.task(
       name="coremarket.tasks.<name>",
       bind=True,
       max_retries=3,
       default_retry_delay=10,
       acks_late=True,
       queue="<queue_name>",
   )
   def my_task(self: Task, ...) -> dict:
       ...
   ```
3. Добавить модуль в `include` список в `celery_app.py`
4. Добавить маршрут в `task_routes` (если очередь не `default`)
5. Вызвать `my_task.delay(...)` из роутера или добавить в `beat_schedule`
