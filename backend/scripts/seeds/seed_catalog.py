"""
Seed script: категории + товары + фото в MinIO.

Идемпотентность:
  - Категория уже имеет image_url → фото НЕ загружается повторно.
  - Категория без image_url → фото загружается, image_url обновляется.
  - Товары уже существуют → не пересоздаются.
  - Товары без галереи → получают фото категории.

Запуск вручную из backend/:
    python scripts/seeds/seed_catalog.py

Автозапуск в Docker — через docker-entrypoint.sh.
"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.backend.application.item.dtos.list_items import ListItemsFilters
from src.backend.config import get_settings
from src.backend.domain.category.entity import Category
from src.backend.domain.item.characteristic import Characteristic
from src.backend.domain.item.entity import Item
from src.backend.domain.item.gallery import Gallery
from src.backend.infrastructure.db.sqlalchemy.blog.repository import SqlAlchemyBlogPostRepository
from src.backend.infrastructure.db.sqlalchemy.category.repository import SqlAlchemyCategoryRepository
from src.backend.infrastructure.db.sqlalchemy.item.repository import (
    SqlAlchemyCharacteristicRepository,
    SqlAlchemyGalleryRepository,
    SqlAlchemyItemRepository,
)
from src.backend.infrastructure.storage.minio.storage import MinIOFileStorage

# Импортируем все модели чтобы SQLAlchemy смог сконфигурировать relationships
import src.backend.infrastructure.db.sqlalchemy.user.model       # noqa: F401
import src.backend.infrastructure.db.sqlalchemy.category.model   # noqa: F401
import src.backend.infrastructure.db.sqlalchemy.item.model       # noqa: F401
import src.backend.infrastructure.db.sqlalchemy.tag.model        # noqa: F401
import src.backend.infrastructure.db.sqlalchemy.comment.model    # noqa: F401
import src.backend.infrastructure.db.sqlalchemy.rating.model     # noqa: F401
import src.backend.infrastructure.db.sqlalchemy.blog.model       # noqa: F401

# (slug, название, описание, файл в media/items/)
CATEGORY_DEFS = [
    ("electronics", "Электроника",  "Смартфоны, ноутбуки и другая бытовая техника", "electro.jpg"),
    ("instruments", "Инструменты",  "Ручной и электрический инструмент",             "instrument.webp"),
    ("furniture",   "Мебель",       "Мебель для дома и офиса",                       "mebel.webp"),
    ("clothing",    "Одежда",       "Одежда, обувь и аксессуары",                    "odejda.jpg"),
    ("sports",      "Спорт",        "Спортивные товары и инвентарь",                 "sport.avif"),
]

# slug → список (name, short_description, description, [(char_name, char_value), ...])
ITEMS_BY_CATEGORY: dict[str, list[tuple]] = {
    "electronics": [
        (
            "Samsung Galaxy S25 Ultra",
            "Флагманский смартфон Samsung с AI-функциями и встроенным S Pen",
            "Samsung Galaxy S25 Ultra задаёт новые стандарты для Android-флагманов. "
            "Snapdragon 8 Elite, камера 200 МП, 10× оптический зум, встроенный стилус S Pen.",
            [("Экран", "6.9\" Dynamic AMOLED 120 Гц"), ("Процессор", "Snapdragon 8 Elite"),
             ("Камера", "200 МП + 50 МП + 10 МП"), ("ОЗУ", "12 ГБ")],
        ),
        (
            "MacBook Air M4",
            "Ультратонкий ноутбук Apple на новом чипе M4 — до 18 часов автономности",
            "MacBook Air на чипе M4 сочетает профессиональную производительность, "
            "вес от 1.24 кг и до 18 часов работы без подзарядки.",
            [("Процессор", "Apple M4"), ("ОЗУ", "16 / 32 ГБ"),
             ("Экран", "13.6\" Liquid Retina"), ("Автономность", "до 18 ч")],
        ),
        (
            "Sony WH-1000XM6",
            "Беспроводные наушники с лучшим в классе шумоподавлением",
            "Sony WH-1000XM6 — топовые беспроводные наушники с активным шумоподавлением "
            "нового поколения, поддержкой LDAC и до 40 часов автономной работы.",
            [("Тип", "Накладные, беспроводные"), ("Автономность", "до 40 ч"),
             ("Кодеки", "LDAC, AAC, SBC"), ("ANC", "Да")],
        ),
    ],
    "instruments": [
        (
            "Makita DHP484Z",
            "Аккумуляторная дрель-шуруповёрт 18В — мощность 54 Нм без аккумулятора",
            "Надёжная дрель-шуруповёрт Makita серии LXT. Крутящий момент 54 Нм, "
            "2 скорости, LED-подсветка рабочей зоны. Продаётся без аккумулятора.",
            [("Напряжение", "18 В"), ("Момент", "54 Нм"),
             ("Скорости", "2"), ("Патрон", "13 мм самозажимной")],
        ),
        (
            "Bosch GSB 12V-15",
            "Компактная ударная дрель Bosch 12В с двумя аккумуляторами в комплекте",
            "Лёгкая и мощная ударная дрель Bosch Professional. Два аккумулятора 2.0 Ач "
            "обеспечивают непрерывную работу. Идеальна для дома и мелкого ремонта.",
            [("Напряжение", "12 В"), ("Патрон", "1/4\""),
             ("Вес", "0.9 кг"), ("Комплект", "2 аккумулятора + ЗУ")],
        ),
        (
            "Stanley FatMax Tape 8м",
            "Профессиональная рулетка 8 м с двойным замком и нейлоновым покрытием",
            "Рулетка Stanley FatMax с двойным замком фиксации, ударопрочным корпусом "
            "и нейлоновым покрытием ленты для долгого срока службы.",
            [("Длина", "8 м"), ("Ширина ленты", "32 мм"),
             ("Покрытие", "Нейлон"), ("Класс точности", "II")],
        ),
    ],
    "furniture": [
        (
            "Кровать MALM 160×200",
            "Двуспальная кровать с 4 ящиками для хранения в стиле минимализм",
            "Кровать MALM с высоким изголовьем и четырьмя вместительными ящиками "
            "под основанием. Шпон ясеня, простая сборка.",
            [("Размер", "160×200 см"), ("Материал", "Шпон ясеня"),
             ("Хранение", "4 ящика"), ("Высота изголовья", "120 см")],
        ),
        (
            "Диван-кровать Milano",
            "Раскладной диван в скандинавском стиле с ортопедическим основанием",
            "Диван Milano с механизмом аккордеон, тканевой обивкой и ортопедическим "
            "пружинным блоком. Подходит для ежедневного сна.",
            [("Размер", "240×96×88 см"), ("Механизм", "Аккордеон"),
             ("Спальное место", "145×195 см"), ("Обивка", "Рогожка")],
        ),
        (
            "Стол письменный Compact",
            "Компактный письменный стол с тумбой на колёсиках",
            "Письменный стол с удобной мобильной тумбой и металлическими ножками. "
            "Минималистичный дизайн вписывается в любой интерьер.",
            [("Размер", "120×60×75 см"), ("Материал", "ЛДСП + металл"),
             ("Тумба", "3 ящика"), ("Колёсики", "С тормозом")],
        ),
    ],
    "clothing": [
        (
            "Nike Air Max 270",
            "Кроссовки с самой высокой воздушной подушкой в линейке Air Max",
            "Nike Air Max 270 — максимальный комфорт благодаря самой большой воздушной "
            "подушке в истории Air Max. Сетчатый верх обеспечивает вентиляцию.",
            [("Тип", "Кроссовки"), ("Подошва", "Air Max 270"),
             ("Верх", "Mesh + синтетика"), ("Назначение", "Повседневные")],
        ),
        (
            "Levi's 501 Original Jeans",
            "Прямые джинсы — классика с 1873 года, 100% хлопок",
            "Оригинальные прямые джинсы Levi's 501 из плотного денима с пятью карманами. "
            "Подходят для любого случая и с годами становятся только лучше.",
            [("Крой", "Прямой"), ("Посадка", "Стандартная"),
             ("Состав", "100% хлопок"), ("Застёжка", "Пуговицы")],
        ),
        (
            "Пуховик Nuptse 700",
            "Тёплый пуховик со стёганым дизайном и гусиным пухом 700-fill",
            "Культовый пуховик Nuptse с 700-fill гусиным пухом. Удерживает тепло "
            "до −20 °C, упаковывается в собственный карман.",
            [("Утеплитель", "Гусиный пух 700-fill"), ("Температура", "до −20 °C"),
             ("Вес", "700 г"), ("Упаковка", "В собственный карман")],
        ),
    ],
    "sports": [
        (
            "Велосипед Trek Marlin 7",
            "Горный велосипед 29\" с гидравлическими тормозами и вилкой RockShox",
            "Trek Marlin 7 — идеальный выбор для горных трасс. Рама Alpha Silver Aluminium, "
            "вилка RockShox Recon, гидравлические дисковые тормоза.",
            [("Колёса", "29\""), ("Вилка", "RockShox Recon 120 мм"),
             ("Тормоза", "Hydraulic Disc"), ("Рама", "Alpha Silver Aluminium")],
        ),
        (
            "Гиря 24 кг Premium",
            "Чугунная гиря с виниловым покрытием — для кетлбол-тренировок",
            "Надёжная чугунная гиря с удобной широкой рукоятью и виниловым покрытием "
            "для защиты пола. Подходит для свингов, толчка и жима.",
            [("Вес", "24 кг"), ("Материал", "Чугун + винил"),
             ("Диаметр рукояти", "35 мм"), ("Основание", "Плоское")],
        ),
        (
            "Ракетка Wilson Pro Staff 97",
            "Контрольная теннисная ракетка для опытных игроков — 315 г",
            "Wilson Pro Staff 97 — ракетка профессионального уровня. Вес 315 г, "
            "площадь головки 630 см², открытая струнная решётка 16×19.",
            [("Площадь головки", "630 см²"), ("Вес", "315 г"),
             ("Длина", "68.5 см"), ("Решётка", "16×19")],
        ),
    ],
}


# (category_slug, post_slug, title, short_description, markdown_content)
BLOG_POSTS_DEFS: list[tuple[str, str, str, str, str]] = [
    (
        "electronics",
        "kak-vybrat-smartfon-2025",
        "Как выбрать смартфон в 2025 году",
        "Разбираем ключевые характеристики: процессор, камера, батарея и дисплей — что важно, а на что не стоит тратить деньги.",
        """\
# Как выбрать смартфон в 2025 году

Рынок смартфонов переполнен предложениями, и выбрать подходящий **без потери денег** становится всё сложнее.
В этой статье разберём ключевые характеристики и расставим приоритеты.

## Процессор: на что смотреть

Флагманские чипы 2025 года:

| Чип | Производитель | Техпроцесс | Баллы AnTuTu |
|-----|---------------|-----------|--------------|
| Snapdragon 8 Elite | Qualcomm | 3 нм | ~2 900 000 |
| Apple A18 Pro | Apple | 3 нм | ~2 800 000 |
| Dimensity 9400 | MediaTek | 3 нм | ~2 700 000 |

> Для повседневных задач хватит любого чипа среднего класса — не переплачивайте за топ ради статуса.

## Камера

Не гонитесь за мегапикселями. Важнее:

- **Размер матрицы** — чем больше, тем лучше съёмка в темноте
- **Оптическая стабилизация (OIS)** — критична для видео
- **Оптический зум** — 3× и выше реально полезен

## Батарея

Минимум для комфортного использования — **4 500 мАч**. Быстрая зарядка от 65 Вт уже стала стандартом.

## Итог

~~Покупайте самое дорогое~~ Определите свой сценарий использования и выберите лучшее в этом бюджете.

- [x] Процессор среднего класса или выше
- [x] OIS в камере
- [ ] Необязательно: оптический зум 5×
""",
    ),
    (
        "instruments",
        "instrumenty-dlya-pervogo-remonta",
        "Инструменты для первого ремонта: минимальный набор",
        "Что купить начинающему мастеру: дрель, лазерный уровень, шуруповёрт и ещё 5 незаменимых вещей.",
        """\
# Инструменты для первого ремонта

Делаете ремонт впервые? Не тратьте деньги на всё сразу.
Вот **минимальный набор**, с которым можно закрыть 90% задач.

## Обязательный набор

| Инструмент | Зачем нужен | Бюджет |
|-----------|-------------|--------|
| Дрель-шуруповёрт | Сверление, вкручивание | от 3 000 ₽ |
| Лазерный уровень | Ровная развеска, укладка | от 2 000 ₽ |
| Рулетка 5 м | Замеры | от 300 ₽ |
| Набор бит | Под любые шурупы | от 500 ₽ |
| Перфоратор | Бетон и кирпич | от 5 000 ₽ |

## Дрель vs Перфоратор

Если в квартире **бетонные стены** — без перфоратора не обойтись.
Обычная дрель в ударном режиме справится только с кирпичом и деревом.

```bash
# Правило подбора сверла
бетон → бур SDS-plus
кирпич/гипс → бур или обычное сверло по бетону
дерево → спиральное сверло по дереву
металл → кобальтовое сверло HSS-Co
```

## Что покупать не нужно сразу

- ~~Строительный пылесос~~ — возьмите в аренду
- ~~Угловая шлифмашина~~ — если нет плиточных работ
- ~~Сварочный аппарат~~ — точно не для первого ремонта

> **Совет:** Аккумуляторный инструмент одного бренда — один аккумулятор на всё.
> Выберите платформу (Makita 18V, Bosch 18V) и придерживайтесь её.
""",
    ),
    (
        "furniture",
        "kak-vybrat-divan-dlya-sna",
        "Как выбрать диван для ежедневного сна",
        "Механизм раскладывания, ортопедическое основание, ткань обивки — объясняем без лишних терминов.",
        """\
# Как выбрать диван для ежедневного сна

Если диван — ваше основное спальное место, к выбору нужно подойти серьёзно.
Неправильный диван → боли в спине → плохой сон → плохое самочувствие.

## Механизм раскладывания

| Механизм | Плюсы | Минусы | Подходит для сна |
|----------|-------|--------|-----------------|
| Аккордеон | Ровное полотно, быстро | Громоздкий | ✓ Да |
| Еврокнижка | Компактный, удобный | Щель посередине | ✓ Да |
| Клик-кляк | Дёшево | Неудобно раскладывать | ✗ Не лучший |
| Дельфин | Изящный | Маленькое спальное место | ✗ Нет |

> Лучший выбор для ежедневного сна — **аккордеон** или **еврокнижка**.

## Наполнитель

- **Пружинный блок** — долговечно, хорошая поддержка спины
- **Пенополиуретан** (ППУ) плотностью **от 35 кг/м³** — минимум для ежедневного использования
- **Холлофайбер** — мягко, но быстро проседает

## Обивка

~~Велюр~~ — красиво, но собирает шерсть домашних животных.

Практичные варианты:
- [x] Рогожка — износостойкая, не скользит
- [x] Микровелюр — мягкий, легко чистится
- [ ] Натуральная кожа — красиво, дорого, холодно зимой
""",
    ),
    (
        "clothing",
        "kapsulnyy-garderob-osnovy",
        "Капсульный гардероб: базовые вещи на все случаи жизни",
        "10 вещей, которые заменят 50 — как собрать гардероб, где всё сочетается между собой.",
        """\
# Капсульный гардероб: базовые вещи

Капсульный гардероб — это набор вещей, которые **легко сочетаются между собой**
и закрывают большинство жизненных ситуаций.

## Базовая капсула: 10 вещей

| Вещь | Цвет | Зачем |
|------|------|-------|
| Белая рубашка | Белый | Офис, вечер, casual |
| Прямые джинсы | Тёмно-синий | Универсальные низы |
| Чёрные брюки | Чёрный | Офис и ужин |
| Серая толстовка | Серый | Повседневный верх |
| Чёрная водолазка | Чёрный | Холодные дни |
| Белая футболка | Белый | Базовый слой |
| Чёрное платье | Чёрный | Любой повод |
| Джинсовая куртка | Синий | Лёгкий верхний слой |
| Кожаные кеды | Белый | Любой низ |
| Лоферы | Чёрный | Офис и smart-casual |

## Принципы выбора

1. **Нейтральные цвета** — белый, чёрный, серый, бежевый, тёмно-синий
2. **Качество > количество** — лучше 1 хорошая вещь, чем 5 плохих
3. **Проверка совместимости** — новая вещь должна сочетаться минимум с 3 уже имеющимися

> ~~"Мне нечего надеть"~~ — фраза, которая исчезнет после сборки капсулы.

## Что точно не нужно в капсуле

- [x] Принты и яркие цвета — оставить 1-2 акцентных вещи
- [ ] Трендовые вещи — они выйдут из моды через сезон
""",
    ),
    (
        "sports",
        "velosiped-dlya-goroda-kak-vybrat",
        "Городской велосипед: как выбрать и не пожалеть",
        "Сравниваем шоссейники, гибриды и горные велосипеды для ежедневных поездок по городу.",
        """\
# Городской велосипед: как выбрать

Велосипед для города — это не горный и не шоссейный.
У них разные задачи, и путаница в этом вопросе стоит денег.

## Типы велосипедов для города

| Тип | Скорость | Комфорт | Бездорожье | Цена |
|-----|---------|---------|-----------|------|
| Шоссейник | ★★★★★ | ★★☆☆☆ | ✗ | Высокая |
| Гибрид | ★★★★☆ | ★★★★☆ | ★★☆☆☆ | Средняя |
| Горный (hardtail) | ★★★☆☆ | ★★★☆☆ | ★★★★★ | Средняя |
| Складной | ★★☆☆☆ | ★★★☆☆ | ✗ | Средняя |

**Вывод:** для города лучший выбор — **гибрид**.

## На что смотреть

### Тормоза
- **Дисковые гидравлические** — лучший вариант, стабильны в дождь
- **Ободные V-brake** — дёшево, достаточно для сухого города
- ~~Барабанные~~ — тяжёлые, слабые, только для прогулочных

### Трансмиссия

```
Планетарная втулка (3-8 скоростей):
  + не требует обслуживания
  + работает в грязь и дождь
  - тяжелее
  - ограничен диапазон

Внешняя (7-11 скоростей):
  + лёгкая
  + широкий диапазон
  - нужна регулярная чистка
```

## Минимальный бюджет

> Хороший городской велосипед начинается от **25 000 ₽**.
> Дешевле — компромисс по надёжности или весу.

- [x] Дисковые тормоза
- [x] Алюминиевая рама
- [ ] Карбоновая вилка — не обязательно для города
""",
    ),
]


async def _get_existing_cat_keys(settings) -> dict[str, str]:
    """Шаг 0: читаем image_url уже существующих категорий из PostgreSQL.

    Возвращает {slug: minio_key} для категорий, которые уже есть в БД.
    Это позволяет на повторных запусках переиспользовать тот же MinIO-ключ
    вместо загрузки дублирующего фото.
    """
    engine = create_async_engine(settings.ASYNC_DATABASE_URL)
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    result: dict[str, str] = {}
    async with factory() as session:
        cat_repo = SqlAlchemyCategoryRepository(session=session)
        for slug, *_ in CATEGORY_DEFS:
            cat = await cat_repo.get_by_slug(slug)
            if cat and cat.image_url:
                result[slug] = cat.image_url
    await engine.dispose()
    return result


async def _upload_photos(media_items_dir: Path, existing_keys: dict[str, str]) -> dict[str, str]:
    """Шаг 1: загружаем фото в MinIO, возвращаем {slug: minio_key}.

    Если категория уже имеет ключ в MinIO (существующая категория),
    переиспользуем его — не загружаем дубликат.
    """
    storage = MinIOFileStorage()
    keys: dict[str, str] = {}
    for slug, name, _desc, photo_filename in CATEGORY_DEFS:
        if slug in existing_keys:
            keys[slug] = existing_keys[slug]
            print(f"[{name}] Переиспользую существующий ключ: {existing_keys[slug]}")
            continue
        photo_path = media_items_dir / photo_filename
        if not photo_path.exists():
            print(f"[WARN] Фото не найдено: {photo_path} — категория '{name}' пропущена")
            continue
        ext = photo_path.suffix.lstrip(".")
        print(f"[{name}] Загружаю {photo_filename}...")
        key = await storage.save(photo_path.read_bytes(), "items", ext)
        keys[slug] = key
        print(f"  ✓ MinIO key: {key}")
    return keys


async def _seed_db(photo_keys: dict[str, str], settings) -> None:
    """Шаг 2: создаём/обновляем категории и товары в PostgreSQL."""
    engine = create_async_engine(settings.ASYNC_DATABASE_URL)
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        cat_repo = SqlAlchemyCategoryRepository(session=session)
        item_repo = SqlAlchemyItemRepository(session=session)
        gallery_repo = SqlAlchemyGalleryRepository(session=session)
        char_repo = SqlAlchemyCharacteristicRepository(session=session)

        for slug, name, description, _photo_filename in CATEGORY_DEFS:
            photo_key = photo_keys.get(slug)
            if photo_key is None:
                continue

            existing_cat = await cat_repo.get_by_slug(slug)

            if existing_cat is None:
                cat = Category.create(name=name, slug=slug, description=description, image_url=photo_key)
                cat = await cat_repo.create(cat)
                print(f"\n  ✓ Категория '{name}' создана")
                is_new_category = True
            else:
                cat = existing_cat
                if cat.image_url != photo_key:
                    cat.change_image_url(photo_key)
                    await cat_repo.update(cat)
                    print(f"\n  ↻ Категория '{name}' — фото обновлено")
                else:
                    print(f"\n  ↻ Категория '{name}' уже существует")
                is_new_category = False

            existing_items = await item_repo.list(ListItemsFilters(category_id=cat.id, limit=1))
            skip_create = bool(existing_items) and not is_new_category
            if skip_create:
                print(f"  ⊘ Новые товары не создаю (уже есть) — проверяю галереи")

            # Добавляем фото существующим товарам без галереи
            all_items = await item_repo.list(ListItemsFilters(category_id=cat.id, limit=1000))
            preview_keys = await gallery_repo.get_preview_keys([i.id for i in all_items])
            patched = 0
            for existing_item in all_items:
                if preview_keys.get(existing_item.id) is None:
                    await gallery_repo.create(Gallery.create(item_id=existing_item.id, image_url=photo_key))
                    patched += 1
            if patched:
                print(f"  ↳ Добавлено фото {patched} товарам без галереи")

            if skip_create:
                continue

            for item_name, short_desc, full_desc, chars in ITEMS_BY_CATEGORY.get(slug, []):
                item = Item.create(
                    name=item_name,
                    short_description=short_desc,
                    description=full_desc,
                    category_id=cat.id,
                    youtube_url=None,
                    marketplace_links=[],
                )
                item.change_is_published(True)
                created = await item_repo.create(item)

                await gallery_repo.create(Gallery.create(item_id=created.id, image_url=photo_key))

                for char_name, char_value in chars:
                    await char_repo.create(
                        Characteristic.create(item_id=created.id, name=char_name, value=char_value)
                    )

                print(f"  + '{item_name}'")

        await session.commit()

    await engine.dispose()


async def _seed_blogs(settings) -> None:
    """Шаг 3: создаём 5 тестовых блог-постов, привязанных к категориям."""
    engine = create_async_engine(settings.ASYNC_DATABASE_URL)
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        cat_repo = SqlAlchemyCategoryRepository(session=session)
        blog_repo = SqlAlchemyBlogPostRepository(session=session)

        for cat_slug, post_slug, title, short_desc, content in BLOG_POSTS_DEFS:
            # Идемпотентность: пропускаем уже существующий пост
            existing = await blog_repo.get_by_slug(post_slug)
            if existing is not None:
                print(f"  ⊘ Пост '{title}' уже существует — пропускаю")
                continue

            cat = await cat_repo.get_by_slug(cat_slug)
            if cat is None:
                print(f"  [WARN] Категория '{cat_slug}' не найдена — пропускаю пост '{title}'")
                continue

            from src.backend.domain.blog.entity import BlogPost as BlogPostEntity
            post = BlogPostEntity.create(title=title, slug=post_slug, short_description=short_desc)
            post.set_content(content)
            post.set_category(cat.id)
            post.publish()

            await blog_repo.create(post)
            print(f"  + Пост '{title}' → категория '{cat_slug}'")

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    settings = get_settings()
    media_items_dir = Path(settings.MEDIA_DIR) / "items"

    # Три отдельных asyncio.run():
    #   0 — asyncpg (чтение существующих ключей из БД)
    #   1 — aioboto3/aiohttp (загрузка фото в MinIO)
    #   2 — asyncpg (запись в БД)
    # Разделение нужно на Windows: aioboto3 (aiohttp) конфликтует с asyncpg
    # при совместном использовании одного event loop.

    print("=== Шаг 0: чтение существующих ключей из БД ===")
    existing_cat_keys: dict[str, str] = asyncio.run(_get_existing_cat_keys(settings))

    print("=== Шаг 1: загрузка фото в MinIO ===")
    photo_keys: dict[str, str] = asyncio.run(_upload_photos(media_items_dir, existing_cat_keys))

    if not photo_keys:
        print("[ERROR] Ни одно фото не загружено — прерываю.")
        sys.exit(1)

    print("\n=== Шаг 2: запись в PostgreSQL ===")
    asyncio.run(_seed_db(photo_keys, settings))

    print("\n=== Шаг 3: блог-посты ===")
    asyncio.run(_seed_blogs(settings))

    print("\n✓ Seed завершён успешно!")
