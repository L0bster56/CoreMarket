# Документация Backend — Сайт каталога товаров / новостей

## Описание проекта

Backend для сайта, предназначенного для отображения:

* товаров
* новостей
* статей
* карточек объектов

Система поддерживает:

* категории
* карточки объектов
* краткое описание
* полное описание
* характеристики
* изображения
* поиск и фильтрацию
* админ-панель
* REST API

---

# Технологический стек

## Рекомендуемый стек

* Python 3.13
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic
* JWT Authentication
* Redis (опционально)
* Docker
* Nginx

---

# Архитектура проекта

```text
backend/
│
├── src/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   │
│   ├── models/
│   │
│   ├── schemas/
│   │
│   ├── repositories/
│   │
│   ├── services/
│   │
│   └── utils/
│
├── alembic/
│
├── tests/
│
├── docker-compose.yml
│
└── README.md
```

---

# Основные сущности

# Category (Категория)

Категория для группировки объектов.

### Примеры:

* Телефоны
* Машины
* Новости
* Технологии

## Поля

| Поле        | Тип      | Описание                 |
| ----------- | -------- | ------------------------ |
| id          | UUID     | Уникальный идентификатор |
| name        | string   | Название категории       |
| slug        | string   | URL-имя                  |
| description | text     | Описание категории       |
| image_url   | string   | Изображение категории    |
| created_at  | datetime | Дата создания            |

---

# Item (Объект / Карточка)

Основная карточка объекта.

## Поля

| Поле              | Тип      | Описание                 |
| ----------------- | -------- | ------------------------ |
| id                | UUID     | Уникальный идентификатор |
| category_id       | UUID     | ID категории             |
| title             | string   | Название                 |
| short_description | string   | Краткое описание         |
| full_description  | text     | Полное описание          |
| preview_image     | string   | Главное изображение      |
| created_at        | datetime | Дата создания            |
| updated_at        | datetime | Дата обновления          |
| is_published      | boolean  | Опубликовано ли          |

---

# Characteristic (Характеристика)

Характеристики объекта.

## Поля

| Поле    | Тип    | Описание                 |
| ------- | ------ | ------------------------ |
| id      | UUID   | Уникальный идентификатор |
| item_id | UUID   | ID объекта               |
| name    | string | Название характеристики  |
| value   | string | Значение                 |

---

# Gallery (Галерея)

Дополнительные изображения объекта.

## Поля

| Поле      | Тип    | Описание                 |
| --------- | ------ | ------------------------ |
| id        | UUID   | Уникальный идентификатор |
| item_id   | UUID   | ID объекта               |
| image_url | string | Ссылка на изображение    |

---

# API Endpoints

## Категории

### Получить список категорий

```http
GET /api/v1/categories
```

### Создать категорию

```http
POST /api/v1/categories
```

### Обновить категорию

```http
PATCH /api/v1/categories/{id}
```

### Удалить категорию

```http
DELETE /api/v1/categories/{id}
```

---

## Объекты / Карточки

### Получить все объекты

```http
GET /api/v1/items
```

### Получить объект по ID

```http
GET /api/v1/items/{id}
```

### Создать объект

```http
POST /api/v1/items
```

### Обновить объект

```http
PATCH /api/v1/items/{id}
```

### Удалить объект

```http
DELETE /api/v1/items/{id}
```

---

# Авторизация

## JWT Authentication

Endpoints:

```http
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

---

# Роли

## Admin

Может:

* создавать категории
* создавать объекты
* редактировать объекты
* удалять объекты
* загружать изображения

## User

Может:

* просматривать контент
* искать
* фильтровать

---

# Безопасность

* JWT авторизация
* Rate Limiting
* Валидация входных данных
* Защита от SQL Injection
* Настройка CORS

---

# Будущие улучшения

* Комментарии
* Лайки
* Избранное
* Elasticsearch
* Теги
* Рекомендации
* Аналитика

---

# Docker

## Запуск проекта

```bash
docker-compose up --build
```

---

# ENV переменные

```env
DATABASE_URL=
SECRET_KEY=
ACCESS_TOKEN_EXPIRE_MINUTES=
REDIS_URL=
```

---
