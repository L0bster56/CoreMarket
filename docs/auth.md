# Аутентификация и роли

## Метод аутентификации

JWT (JSON Web Token). Токен передаётся в заголовке:

```
Authorization: Bearer <token>
```

## Роли

### Admin

- Создавать / редактировать / удалять категории и объекты
- Управлять тегами объектов, характеристиками, галереей
- Загружать изображения в MinIO (`POST /upload`)
- Удалять любые комментарии
- Управлять пользователями
- Полный CRUD блог-постов: создание, публикация, архивация
- Управлять тегами блога и ссылками на товары в постах
- Запускать полный переиндекс Elasticsearch (`POST /search/reindex`)
- Устанавливать `view_count` вручную через `PATCH /items/{id}`

### User

- Просматривать контент
- Искать и фильтровать (SQL и Elasticsearch)
- Оставлять и редактировать свои комментарии
- Удалять свои комментарии
- Ставить и изменять оценку объектам (1–5)

### Public (без авторизации)

- Просматривать объекты, категории, теги
- Читать комментарии
- Смотреть рейтинг объектов
- Читать блог-посты
- Получать presigned URL для изображений (`POST /storage/presigned-urls`)
- Использовать поиск и автодополнение (`GET /search/items`, `GET /search/suggestions`)
- Получать homepage данные (`GET /homepage`)

---

## JWT токены

| Токен           | Срок жизни     | Назначение                          |
|-----------------|----------------|-------------------------------------|
| Access token    | 30 минут       | Авторизация запросов                |
| Refresh token   | 7 дней         | Получение нового access token       |

**Флоу обновления:**
```
Access token истёк (401)
    ↓
POST /auth/refresh  { "refresh_token": "..." }
    ↓
{ "access_token": "...", "refresh_token": "..." }
```

Frontend (`src/lib/api.ts`) перехватывает 401 и автоматически вызывает refresh-on-401. При неудаче — разлогинивает пользователя.

---

## Безопасность

### Контроль доступа

- JWT авторизация (access token + refresh token)
- Роли проверяются в `application/auth/dependencies.py` через `require_admin` и `get_current_user`
- Проверка владельца ресурса для User-уровня (комментарии, оценки)

### Rate Limiting

slowapi ограничивает auth-эндпоинты для предотвращения brute force:

| Эндпоинт          | Лимит            |
|--------------------|------------------|
| `POST /auth/login` | 5 запросов/минуту |
| `POST /auth/register` | 5 запросов/минуту |

При превышении: `429 Too Many Requests` → `{ "detail": "5 per 1 minute" }`.

### Хранилище паролей

- Хэширование: bcrypt (`BcryptHasher`, `infrastructure/security/bcrypt/hasher.py`)
- Пароли никогда не хранятся в открытом виде

### Защита данных

- Валидация входных данных: Pydantic v2 (все body + query params)
- Защита от SQL Injection: SQLAlchemy ORM (параметризованные запросы)
- MinIO bucket: приватный (`anonymous access = none`), доступ только через presigned URLs (TTL 3600с)
- CORS: `CORS_ORIGINS` из ENV

### Security Headers (Nginx)

| Header                    | Значение                                  |
|---------------------------|-------------------------------------------|
| `X-Frame-Options`         | `SAMEORIGIN`                              |
| `X-Content-Type-Options`  | `nosniff`                                 |
| `Referrer-Policy`         | `strict-origin-when-cross-origin`         |
| `Permissions-Policy`      | `camera=(), microphone=(), geolocation=()`|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` (HTTPS) |

---

## Async: email после регистрации

`POST /auth/register` после успешного создания пользователя запускает фоновую Celery-задачу:

```python
send_welcome_email.delay(str(result.user_id))
```

- HTTP-ответ (201) возвращается клиенту немедленно — не ждёт отправки письма
- Задача в очереди `emails` с 3 retries (exponential backoff: 60с → 120с → 240с)
- Если `SMTP_HOST` не задан — задача логирует `email_skipped` без ошибки
- При отказе SMTP — retry, финальный failure логируется в Loki/Grafana

---

## Observability — трассировка auth-запросов

### OpenTelemetry трейсы

Каждый HTTP-запрос к auth-эндпоинтам автоматически создаёт span через OTel FastAPI instrumentation:

```
POST /auth/login
  └─ span: fastapi.request
       ├─ span: sqlalchemy.query (SELECT users WHERE email=...)
       └─ duration: 18ms
```

Трейсы отправляются в Tempo (OTLP gRPC:4317) и доступны в Grafana для анализа.

### Structured Logs (Loki)

`LoggingMiddleware` добавляет `trace_id` и `span_id` в каждую запись лога. Auth-запросы логируются в JSON:

```json
{
  "ts": "2026-06-26T10:00:00Z",
  "level": "INFO",
  "logger": "coremarket.middleware.logging",
  "method": "POST",
  "path": "/api/v1/auth/login",
  "status_code": 200,
  "duration_ms": 45,
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7"
}
```

```json
{
  "ts": "2026-06-26T10:00:01Z",
  "level": "WARNING",
  "logger": "coremarket.middleware.logging",
  "method": "POST",
  "path": "/api/v1/auth/login",
  "status_code": 401,
  "duration_ms": 12,
  "trace_id": "7b3a9c2f1e4d5a6b..."
}
```

### Prometheus-метрики

HTTP-метрики собираются `MetricsMiddleware` автоматически для всех эндпоинтов включая auth:

| Метрика                                    | Что показывает для auth                       |
|--------------------------------------------|-----------------------------------------------|
| `coremarket_http_requests_total`           | Counter login/register успехи и ошибки        |
| `coremarket_http_request_duration_seconds` | Histogram: латентность bcrypt verify          |
| `coremarket_http_requests_in_progress`     | Gauge активных auth-запросов                  |

**LogQL для анализа auth в Grafana:**

```logql
# Все неудачные входы (401)
{compose_service="backend"} | json | path="/api/v1/auth/login" | status_code=401

# Rate limit срабатывания
{compose_service="backend"} | json | status_code=429

# Регистрации за последний час
{compose_service="backend"} | json | path="/api/v1/auth/register" | status_code=201
```

### Drill-down: Loki → Tempo

Из Grafana Loki можно перейти к конкретному трейсу: кликнуть по строке лога → "View in Tempo" (cross-data-source link по `trace_id`). Это позволяет видеть точные span-времена для медленных запросов к БД.
