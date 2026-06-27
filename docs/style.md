# Стиль кода — CoreMarket Backend

## Общие принципы

- Язык кода — **английский** (переменные, методы, классы, файлы).
- Язык документации — **русский** (docstrings, комментарии).
- Никаких `from __future__ import annotations`.
- Импорты группируются в порядке: stdlib → сторонние библиотеки → локальные (`src.backend.*`). Между группами — пустая строка.

---

## Domain — сущности (Entity)

```python
@dataclass(eq=False)                          # eq=False обязателен, иначе dataclass перекроет __eq__ из BaseEntity
class MyEntity(BaseEntity, TimeActionMixin):  # TimeActionMixin — только если нужны временные метки
    field_a: str
    field_b: int
    optional_field: str | None = None

    @classmethod
    def create(cls, field_a: str, field_b: int) -> "MyEntity":
        return cls(field_a=field_a, field_b=field_b)

    def change_field_a(self, field_a: str) -> None:
        self.field_a = field_a
        self.touch()   # только если есть TimeActionMixin
```

**Правила:**
- Все сущности наследуют `BaseEntity` (даёт `id: UUID` и `__eq__`/`__hash__` по id).
- Фабричный метод всегда называется `create(...)` и является `@classmethod`.
- Методы изменения называются `change_<поле>(self, value)`.
- `touch()` вызывается в каждом `change_*` методе.
- `@dataclass(eq=False)` — обязателен на каждом подклассе, иначе `@dataclass` сгенерирует свой `__eq__` по всем полям и сломает сравнение по id.

---

## Domain — Value Objects (VO)

```python
@dataclass(frozen=True)          # frozen=True обязателен для VO
class MyVO:
    value: str

    def __post_init__(self):
        if not self._is_valid():
            raise InvalidMyVOError()

    def _is_valid(self) -> bool:  # приватный метод (_), не double-underscore (__)
        return bool(re.match(r"...", self.value))

    def __str__(self) -> str:
        return self.value
```

**Правила:**
- `frozen=True` — обязателен.
- Валидация — в `__post_init__`, делегируется `_is_valid()`.
- `_is_valid()` — одиночный underscore (не `__is_valid`).
- `__str__` — всегда возвращает `self.value`.
- Ошибка валидации — отдельный класс в соседнем файле `error.py`.

---

## Domain — ошибки

```python
# domain/shared/errors.py
class DomainError(Exception):
    """Базовая ошибка domain слоя"""

class PermissionDeniedError(DomainError):
    """Вызывается когда доступ запрещен"""
```

**Правила:**
- Все domain ошибки наследуют `DomainError`.
- Каждая ошибка — отдельный класс с docstring.
- Специфичные ошибки сущности живут в `domain/<entity>/error.py`.
- Тело класса — только docstring, без `pass`.

---

## Application — Repository Protocol

```python
# application/<entity>/repository.py
from typing import Protocol
from uuid import UUID

class MyEntityRepository(Protocol):
    async def get_by_id(self, entity_id: UUID) -> MyEntity: ...
    async def get_by_slug(self, slug: str) -> MyEntity: ...
    async def create(self, entity: MyEntity) -> MyEntity: ...
    async def update(self, entity: MyEntity) -> None: ...
    async def delete(self, entity: MyEntity) -> None: ...
    async def exists_slug(self, slug: str) -> bool: ...
```

**Правила:**
- Используется `Protocol` (не ABC).
- Все методы — `async`.
- Тело каждого метода — `...` (многоточие).
- Нет `pass`, нет `raise NotImplementedError`.
- `exists_<поле>` методы для проверки уникальности.

---

## Application — Use Cases

```python
# application/<domain>/use_cases/<action>.py
from dataclasses import dataclass

@dataclass
class MyActionUseCase:
    """
    UseCase: краткое описание на русском.

    Ответственность:
        - пункт 1
        - пункт 2
    """
    uow: UnitOfWork
    some_repo: MyEntityRepository

    async def execute(self, cmd: MyActionCommand) -> MyActionResult:
        """
        Args:
            cmd (MyActionCommand): описание

        Returns:
            MyActionResult: описание

        Raises:
            NotFoundError: если сущность не найдена
            SomeError: когда и почему
        """
        async with self.uow:
            entity = await self.some_repo.get_by_id(cmd.entity_id)
            if entity is None:
                raise NotFoundError(f"MyEntity {cmd.entity_id} not found")

            entity.change_field_a(cmd.field_a)

            await self.some_repo.update(entity)
            await self.uow.commit()
            return MyActionResult(id=entity.id, field_a=str(entity.field_a))
```

**Правила:**
- Use case — `@dataclass`, зависимости — поля класса.
- Единственный публичный метод — `async def execute(self, cmd)`.
- Репозитории доступны только через `self.uow.<repo>` — не хранить repo как отдельное поле.
- Если `get_by_id` вернул `None` — сразу `raise NotFoundError(...)`, не продолжать.
- Паттерн `async with self.uow:` для транзакций.
- `flush()` не вызывается напрямую — это забота репозитория.
- Docstring на русском: класс описывает ответственность, метод — Args/Returns/Raises.

### User injection — защищённые use cases

`user: User` передаётся как **поле use case dataclass**, а не через DTO команду. Presentation layer резолвит User из JWT один раз и передаёт при создании use case:

```python
@dataclass
class CreateCommentUseCase:
    uow: UnitOfWork
    user: User          # ← поле use case, инжектируется из presentation

    async def execute(self, cmd: CreateCommentCommand) -> CreateCommentResult:
        async with self.uow:
            comment = Comment.create(
                item_id=cmd.item_id,
                user_id=self.user.id,   # ← self.user, не cmd.user_id
                body=cmd.body,
            )
            ...

# Команда содержит только бизнес-данные — БЕЗ user/user_id
@dataclass
class CreateCommentCommand:
    item_id: UUID
    body: str
    parent_id: UUID | None = None

# Presentation создаёт use case так:
# CreateCommentUseCase(uow=uow, user=current_user).execute(cmd)
```

Проверка роли для admin-only use cases:

```python
@dataclass
class CreateItemUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: CreateItemCommand) -> CreateItemResult:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can create items")
        # проверка роли — ДО открытия uow
        async with self.uow:
            ...
```

---

## Application — DTOs

```python
# application/<domain>/dtos/<action>.py
from dataclasses import dataclass

@dataclass
class MyActionCommand:
    field_a: str
    field_b: int

@dataclass
class MyActionResult:
    id: UUID
    field_a: str
```

**Правила:**
- `Command` — входные данные для use case.
- `Result` — выходные данные.
- `@dataclass`, без `frozen=True` (не VO).
- Живут в `application/<domain>/dtos/`.

---

## Application — ошибки

```python
# application/shared/errors.py
class ApplicationError(Exception):
    """Базовая ошибка слоя Application"""

class NotFoundError(ApplicationError):
    pass

class ConflictError(ApplicationError):
    pass
```

**Правила:**
- Все app-ошибки наследуют `ApplicationError(Exception)`.
- Тело — `pass` (в отличие от domain, где docstring).
- Специфичные ошибки модуля — в `application/<module>/errors.py`.

---

## Infrastructure — SQLAlchemy модели

```python
# infrastructure/db/sqlalchemy/<entity>/model.py
from sqlalchemy import Column, String, Text, UUID, ForeignKey, Boolean

class MyEntityModel(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = 'my_entities'

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    foreign_id = Column(UUID(as_uuid=True), ForeignKey('other.id'), nullable=False)
```

**Правила:**
- Без `Mapped[]` аннотаций — классический стиль через `Column(...)`.
- Порядок миксинов: `Base` → `UUIDMixin` → `TimeStampMixin` → `ActiveMixin` (если нужно).
- `nullable=False` или `nullable=True` явно на каждой колонке.
- `__tablename__` — множественное число, snake_case.
- `UUID(as_uuid=True)` для всех UUID-полей.
- Каждая сущность — в своём файле `<entity>/model.py`. `core/models.py` содержит только `Base`.

### Relationships

```python
class ItemModel(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = 'items'
    ...
    # backref — одна сторона объявляет, другая получает автоматически
    characteristics = relationship(
        'CharacteristicModel',
        backref='item',            # ← CharacteristicModel.item создаётся автоматически
        lazy='selectin',           # ← всегда selectin
        cascade='all, delete-orphan',
    )
    tags = relationship(
        'TagModel',
        secondary=item_tags,       # ← M2M через ассоциативную Table
        backref='items',
        lazy='selectin',
    )

# Дочерняя модель — НЕ объявляет обратную сторону
class CharacteristicModel(Base, UUIDMixin):
    __tablename__ = 'characteristics'
    item_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    # item = relationship(...)  ← НЕ НУЖНО, приходит через backref
```

**Правила relationships:**
- `backref=` вместо `back_populates=` — только одна сторона объявляет.
- `lazy='selectin'` на всех relationships — загружает одним дополнительным SELECT.
- `ondelete='CASCADE'` на FK дочерних таблиц.
- M2M ассоциативная таблица — через `Table(...)` (не класс-модель), живёт в файле основной сущности.
- Самореференция (Comment → children): `foreign_keys='CommentModel.parent_id'` обязателен.

---

## Infrastructure — Маперы

```python
# infrastructure/db/sqlalchemy/<entity>/mapper.py

def to_model(entity: MyEntity) -> MyEntityModel:
    return MyEntityModel(
        id=entity.id,
        name=str(entity.name),   # VO → str через str()
        slug=str(entity.slug),
        ...
    )

def to_entity(model: MyEntityModel) -> MyEntity:
    return MyEntity(
        id=model.id,
        name=Name(model.name),   # str → VO через конструктор
        slug=Slug(model.slug),
        ...
    )
```

**Правила:**
- Две функции: `to_model` и `to_entity`.
- VO конвертируется в `str` через `str(vo)` (поэтому у всех VO есть `__str__`).
- При восстановлении из модели — создание VO через конструктор.
- Явная передача всех полей, включая `id`, `created_at`, `updated_at`.

---

## Infrastructure — Репозитории

```python
# infrastructure/db/sqlalchemy/<entity>/repository.py

class SqlAlchemyMyEntityRepository(SqlAlchemyRepository, MyEntityRepository):

    async def get_by_id(self, entity_id: UUID) -> MyEntity | None:
        stmt = select(MyEntityModel).where(MyEntityModel.id == entity_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_entity(model) if model else None

    async def create(self, entity: MyEntity) -> MyEntity:
        model = to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return to_entity(model)

    async def update(self, entity: MyEntity) -> None:
        model = to_model(entity)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, entity: MyEntity) -> None:
        stmt = delete(MyEntityModel).where(MyEntityModel.id == entity.id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def exists_slug(self, slug: str, exclude_id: UUID = None) -> bool:
        condition = MyEntityModel.slug == slug
        if exclude_id:
            condition = condition & (MyEntityModel.id != exclude_id)
        stmt = select(exists().where(condition))
        result = await self.session.execute(stmt)
        return result.scalar()
```

**Правила:**
- Наследует и `SqlAlchemyRepository`, и Protocol-интерфейс.
- `scalar_one_or_none()` — для запросов 0 или 1 результат.
- `flush()` после каждой мутации (не `commit` — это задача UoW).
- `exists_<поле>` через `select(exists().where(...))`.
- Паттерн `condition = condition & (...)` для optional exclude_id.

---

## Структура директорий (сводка)

```
domain/<entity>/
    entity.py           ← @dataclass(eq=False), create(), change_*()
    error.py            ← специфичные DomainError подклассы
    value_objects/
        <vo_name>/
            value_object.py   ← @dataclass(frozen=True), _is_valid(), __str__
            error.py

application/<entity>/
    repository.py       ← Protocol с async методами
    dtos/
        <action>.py     ← Command + Result @dataclass
    use_cases/
        <action>.py     ← @dataclass UseCase с execute()

infrastructure/db/sqlalchemy/<entity>/
    model.py            ← Column-стиль, без Mapped[]
    mapper.py           ← to_model() + to_entity()
    repository.py       ← SqlAlchemyXxxRepository
```

---

---

## Presentation — структура директорий

```
presentation/api/v1/
    core/
        dependencies.py      ← get_db, get_uow, UoWDep
        schemas.py           ← ExceptionSchema
        handlers/
            not_found.py     ← NotFoundError → 404
            conflict.py      ← ConflictError → 409
            bad_request.py   ← BadRequestError → 400
            auth.py          ← NotAuthorizedError + JWTError → 401
    auth/
        router.py            ← /auth/login, /refresh, /me, /change-password
        dependencies.py      ← get_current_user, CurrentUserDep, get_hasher, get_token_service
    <module>/
        router.py            ← @router эндпоинты
        dependencies.py      ← фабрики use cases, XxxDep, get_current_<entity>
```

---

## Presentation — core/dependencies.py

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_uow(
        session: AsyncSession = Depends(get_db)
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session=session)


UoWDep = Annotated[
    SqlAlchemyUnitOfWork,
    Depends(get_uow),
]
```

**Правила:**
- `get_db` — async-генератор с `async with async_session()`, без try/finally.
- `get_uow` получает сессию через `Depends(get_db)`, создаёт `SqlAlchemyUnitOfWork`.
- `UoWDep` — `Annotated` алиас для инъекции UoW без повторения `Depends(get_uow)` везде.

---

## Presentation — auth/dependencies.py

```python
schema = HTTPBearer()


async def get_hasher() -> Argon2Hasher:
    return Argon2Hasher()


async def get_token_service() -> JWTTokenService:
    return JWTTokenService()


async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(schema),
        tokens: JWTTokenService = Depends(get_token_service),
        uow: SqlAlchemyUnitOfWork = Depends(get_uow)
) -> User:
    uc = GetMeUseCase(uow, tokens)
    user = await uc.execute(cmd=GetMeCommand(token=token.credentials))
    return user


CurrentUserDep = Annotated[
    User,
    Depends(get_current_user),
]
```

**Правила:**
- `HTTPBearer()` — глобальный экземпляр схемы, не пересоздаётся.
- `get_current_user` резолвит `User` через `GetMeUseCase`, не декодирует JWT напрямую.
- `CurrentUserDep` — алиас, используется во всех модулях где нужен залогиненный пользователь.

---

## Presentation — module/dependencies.py

Паттерн для каждого модуля: **фабричная функция → `Annotated` алиас**.

```python
# 1. Репозиторий (если нужен вне UoW — для get_current_<entity>)
async def get_item_repo(
        session: AsyncSession = Depends(get_db),
) -> SqlAlchemyItemRepository:
    return SqlAlchemyItemRepository(session=session)

ItemRepoDep = Annotated[SqlAlchemyItemRepository, Depends(get_item_repo)]


# 2. Текущий объект по ID из path-параметра
async def get_current_item(
        item_id: UUID,
        repo: ItemRepoDep
) -> Item:
    item = await repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

CurrentItemDep = Annotated[Item, Depends(get_current_item)]


# 3. Фабрика use case → алиас
def get_create_item_use_case(
        uow: UoWDep,
        user: CurrentUserDep,
) -> CreateItemUseCase:
    return CreateItemUseCase(uow=uow, user=user)

CreateItemDep = Annotated[CreateItemUseCase, Depends(get_create_item_use_case)]


# Use case с текущим объектом
def get_update_item_use_case(
        uow: UoWDep,
        user: CurrentUserDep,
        item: CurrentItemDep,
) -> UpdateItemUseCase:
    return UpdateItemUseCase(uow=uow, user=user, item=item)

UpdateItemDep = Annotated[UpdateItemUseCase, Depends(get_update_item_use_case)]
```

**Правила:**
- Каждый use case — отдельная фабричная функция + `Annotated` алиас.
- `CurrentXxxDep` — резолвит entity из path-параметра через репозиторий, бросает `HTTPException(404)` если не найден.
- Use cases, требующие текущий объект, принимают `CurrentXxxDep` — FastAPI сам разруливает порядок.
- Функции без `async` если нет I/O (простая сборка объекта).

---

## Presentation — module/router.py

Два стиля используются в зависимости от сложности:

### Стиль 1 — функции (простой модуль, без общих class-level deps)

```python
router = APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def list_items(
        uc: ListItemDep,
        search: str | None = Query(default=None),
        category_id: UUID | None = Query(default=None),
        limit: int = Query(default=20),
        offset: int = Query(default=0),
):
    cmd = ListItemsCommand(search=search, category_id=category_id, limit=limit, offset=offset)
    return await uc.execute(cmd)


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
async def get_item(item_id: UUID, uc: GetItemDep):
    return await uc.execute(GetItemCommand(item_id=item_id))


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CreateItemResult)
async def create_item(cmd: CreateItemCommand, uc: CreateItemDep):
    return await uc.execute(cmd)


@router.patch("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_item(cmd: UpdateItemCommand, uc: UpdateItemDep):
    await uc.execute(cmd)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(uc: DeleteItemDep):
    await uc.execute()
```

### Стиль 2 — CBV (`@cbv`) — когда нужны общие class-level зависимости

```python
from fastapi_utils.cbv import cbv

router = APIRouter(prefix="/auth", tags=["auth"])


@cbv(router)
class AuthRouter:
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)  # ← общая deps

    @router.post("/login", status_code=status.HTTP_201_CREATED, response_model=LoginUserResult)
    async def login(
            self,
            request: LoginUserCommand,
            hasher: Argon2Hasher = Depends(get_hasher),
            tokens: JWTTokenService = Depends(get_token_service),
    ):
        uc = LoginUserUseCase(uow=self.uow, tokens=tokens, hasher=hasher)
        return await uc.execute(cmd=request)
```

**Правила:**
- Предпочтительный стиль — **функции** (Стиль 1): use case приходит как `XxxDep`, роутер просто вызывает `uc.execute(cmd)`.
- `@cbv` — когда у всех методов класса одна и та же `uow` или `user` зависимость.
- `APIRouter` объявляется с `prefix` и `tags`.
- `responses={}` на роутере для общих ошибок модуля (например, `401` для auth).
- Status codes: `GET` → `200`, `POST` → `201`, `PATCH/DELETE без тела` → `204`.
- `response_model=` — только если возвращаем тело; для `204` не указывается.

---

## Presentation — exception handlers

```python
# core/handlers/not_found.py
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "status_code": status.HTTP_404_NOT_FOUND}
    )
```

| Файл | Исключение | HTTP-код |
|---|---|---|
| `not_found.py` | `NotFoundError` | 404 |
| `conflict.py` | `ConflictError` | 409 |
| `bad_request.py` | `BadRequestError` | 400 |
| `auth.py` | `NotAuthorizedError`, `JWTError` | 401 |

**Правила:**
- Один handler на тип ошибки, в отдельном файле.
- Тело ответа всегда `{"detail": str(exc), "status_code": <код>}`.
- `JWTError` → 401 с фиксированным `detail: "Invalid credentials"`.
- Handlers регистрируются в `main.py`: `app.add_exception_handler(XxxError, xxx_handler)`.

---

## Presentation — schemas.py

```python
class ExceptionSchema(BaseModel):
    detail: str | dict
    status_code: int
```

- Используется в `responses={}` роутеров как `"model": ExceptionSchema`.
- Response schemas для данных — либо `Result` DTO из application (если совместим с Pydantic), либо отдельный `XxxResponse(BaseModel)` в `schemas.py` модуля.

---

## Замеченные непоследовательности (не исправлять без согласования)

| Файл | Проблема |
|---|---|
| `user/value_objects/username/value_object.py` | `@dataclass` без `frozen=True` (у Email и Slug есть) |
| `domain/shared/value_objects/email/value_object.py` | `__is_valid` (двойной underscore) вместо `_is_valid` |
| `domain/rating/value_objects/score.py` | нет `__str__` |
