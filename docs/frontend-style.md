# Frontend Style Guide — CoreMarket

> Этот документ описывает реальный UI/UX и визуальные паттерны frontend. Backend code style — в [style.md](style.md).

---

## Дизайн-философия

CoreMarket придерживается **premium marketplace** эстетики: чистый SaaS-интерфейс без визуального шума, где контент (товары, изображения, рейтинги) — на первом плане.

Ключевые принципы:

- **Minimalism первичен** — белые фоны, воздушные отступы, ничего лишнего в карточках
- **Perceived performance** важнее реальной — skeleton loading появляется мгновенно, контент стримится под него
- **Subtle motion** — анимации подтверждают действие, не развлекают
- **Consistent elevation** — shadow-sm / shadow-xl только через hover, не как декор

---

## Цветовая палитра

Основная палитра — глубокие navy-тона, определены в `globals.css` через `@theme`:

| Токен             | HEX       | Применение                                    |
| ----------------- | --------- | --------------------------------------------- |
| `indigo-800`      | `#031E36` | Основной текст, самый тёмный фон (hero)       |
| `indigo-600`      | `#04335A` | Primary кнопки, логотип, активные состояния   |
| `indigo-500`      | `#4474A3` | Hover-состояния, focus-ring, secondary акцент |
| `indigo-300`      | `#9ABCED` | Теги, progress bar gradient, placeholder      |
| `indigo-100`      | `#C4D4E6` | Бледные фоны карточек, gradient fill-placeholders |
| `indigo-50`       | `#eef3f9` | Активный nav-item, очень лёгкие фоны          |
| `--background`    | `#f0f5fb` | Страничный фон (глобальный `body`)            |

> Amber (`text-amber-400`) — единственный off-palette цвет, используется только для звёзд рейтинга.

### Gradient patterns

Три повторяющихся паттерна:

```
Hero орб (blur): bg-[#04335A] blur-[140px] opacity-80  — главный свет
Accent орб:      bg-[#4474A3] blur-[100px] opacity-20  — правый угол
Highlight орб:   bg-[#9ABCED] blur-[100px] opacity-10  — левый край
```

CTA-блок: `from-[#031E36] via-[#04335A] to-[#4474A3]` — диагональный gradient.  
Image placeholder: `from-[#eef3f9] to-[#C4D4E6]` — gradient вместо серого фона.

---

## Типографика

- **Шрифт:** Geist Sans (переменная `--font-geist-sans`), fallback `system-ui, sans-serif`
- **Mono:** Geist Mono — только для code-блоков в блог-постах

### Иерархия заголовков на странице

| Уровень       | Классы                                      | Контекст                  |
| ------------- | ------------------------------------------- | ------------------------- |
| Hero H1       | `text-4xl sm:text-5xl lg:text-6xl font-bold text-white` | Главная страница           |
| Section H2    | `text-2xl sm:text-3xl font-bold text-[#031E36]` | Секции категорий/trending |
| Card H3       | `font-bold text-[#031E36] text-base leading-snug line-clamp-2` | ItemCard                  |
| Section label | `text-[#4474A3] font-semibold text-xs tracking-widest uppercase` | над H2 в секциях           |
| Body          | `text-sm text-gray-500 leading-relaxed`     | short_description          |

---

## Layout

Максимальная ширина контента: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`.

Breakpoints (Tailwind defaults, mobile-first):
- `sm` = 640px — переход от stack к grid
- `lg` = 1024px — sidebar появляется в каталоге/блоге
- `xl` = 1280px — расширенная сетка (3→4 колонки)

### Типичные grid-паттерны

| Страница          | Mobile    | sm       | lg       |
| ----------------- | --------- | -------- | -------- |
| Главная / trending | 1 col     | 2 col    | 3 col    |
| Каталог (карточки) | 1 col    | 2 col    | 3 col    |
| Item detail        | stack     | stack    | 2-col    |
| Recommended        | horizontal scroll | 2 col | 4 col |

---

## Компоненты

### Header

Sticky: `sticky top-0 z-50 bg-white/85 backdrop-blur-xl border-b border-gray-200/60`

- Logo: маленький gradient-квадрат (`rounded-xl from-[#04335A] to-[#4474A3]`) + bold текст
- Nav: `rounded-xl` пункты, активный — `bg-[#eef3f9] text-[#04335A]`
- Auth-кнопки: "Войти" текстовая, "Регистрация" — solid navy `rounded-xl`
- Mobile: burger-меню с inline drawer (без overlay), `md:hidden`

### ItemCard

`rounded-3xl shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300`

Зоны:
1. **Image (h-60)** — gradient placeholder → shimmer skeleton → fade-in image при `onLoad`
2. **Category badge** — `backdrop-blur-sm bg-white/90`, top-left
3. **YouTube badge** — красный `bg-red-600 rounded-full`, top-right
4. **Tag pills** — `bg-[#04335A]/80 backdrop-blur-sm`, bottom-left overlay (max 2 тега)
5. **Gradient overlay** — `from-black/20 to-transparent h-16` поверх изображения
6. **Content** — `p-5`, title + description + rating/views footer

Hover: image `scale-105 duration-500` + card lift `-translate-y-1 shadow-xl`.

Image loading: shimmer placeholder (`className="skeleton"`) удаляется после `onLoad`, image fade-in: `opacity-0 → opacity-100`.

### CategoryCard

`rounded-2xl bg-gray-900 aspect-video` — тёмный фон с image fill.  
Overlay: `bg-gradient-to-t from-black/80 to-transparent` — текст всегда читаем.  
Hover: `ring-2 ring-indigo-500`, image `opacity-60 → scale-105`.

Image resolving — client-side через `getCachedOrFetch` (presigned URL с кэшем 45 мин).

### GalleryViewer

`aspect-video rounded-2xl` главное изображение + горизонтальный скролл thumbnail-полосы.  
Активный thumbnail: `ring-2 ring-indigo-600 ring-offset-1`.  
Главное: `fetchPriority="high" decoding="async"` — LCP оптимизация.

### SearchBar

`rounded-2xl` контейнер: `focus-within:border-[#9ABCED] focus-within:shadow-md transition-all`.  
Кнопка: `bg-[#04335A] hover:bg-[#031E36] rounded-xl`.  
Submit — нативный `<form action="/catalog" method="GET">`, без JS.

### RatingWidget

Два режима в одном компоненте:

- **Статический** (для всех): amber звёзды + число `X.X (N)` 
- **Интерактивный** (для auth users): hover-highlight + optimistic update

Optimistic: `setUserScore(score)` до async вызова API, rollback `setUserScore(prevScore)` при ошибке.

### RecommendedProducts

Адаптивный: мобильный — `flex overflow-x-auto snap-x snap-mandatory` (horizontal scroll с `snap-start` карточками w-72), десктоп — 4-col grid.

Async Server Component: параллельно `getRecommendations()` + `serverGetPresignedUrls()`.

### NavigationProgress

Тонкая 2px progress bar фиксирована поверх всего (`fixed top-0 z-[9999]`).  
Градиент: `from-[#4474A3] via-[#9ABCED] to-[#4474A3]`.  
Glow: второй слой `-6px h-[6px] via-[#9ABCED]/30` размытый блеск под линией.

Три состояния: `idle` (hidden) → `growing` (`.progress-growing` animation) → `complete` (100% width → fade out → idle).

Запуск: перехват click на `a[href]` (только internal, без hash, без download).

---

## Loading UX

### Принципы

1. Skeleton точно воспроизводит layout реального контента — не generic пульсирующие блоки
2. Каждая страница имеет собственный `loading.tsx` с секциями под реальную структуру
3. Skeleton появляется мгновенно (static shell) — пользователь видит структуру, не белый экран

### Skeleton компоненты

Два переиспользуемых примитива в каждом `loading.tsx`:

```tsx
function S({ className = '' }) {     // pill-форма (текст, заголовки)
  return <div className={`skeleton rounded-full ${className}`} />
}
function SBox({ className = '' }) {  // прямоугольник (изображения, блоки)
  return <div className={`skeleton rounded-2xl ${className}`} />
}
```

### CSS shimmer (globals.css)

```css
.skeleton {
  background: linear-gradient(
    90deg,
    #e8f0f8 0%, #ddeaf5 35%, #cddff0 50%, #ddeaf5 65%, #e8f0f8 100%
  );
  background-size: 800px 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}
```

Цвета shimmer — из палитры (`indigo-100`/`indigo-50` тона). Не нейтральный серый.

### Покрытие loading.tsx

| Route                    | Секции в skeleton                                    |
| ------------------------ | ---------------------------------------------------- |
| `/` (homepage)           | hero с search, categories row, 6 product cards, 3 blog cards |
| `/catalog`               | sidebar (3 блока) + 9 card grid + search bar        |
| `/catalog/[category]`    | аналогично `/catalog`                               |
| `/items/[id]`            | breadcrumb + gallery (aspect-video + thumbnails) + info + characteristics table + 4 recommended + 3 comments |
| `/blog`                  | sidebar (categories + tags) + 6 blog card grid      |
| `/blog/[slug]`           | hero cover + title + content lines                  |
| `/tags/[slug]`           | header + card grid                                  |

### Suspense на homepage

Homepage использует per-section Suspense вместо полного `loading.tsx`:

```tsx
// Hero — static shell, рендерится мгновенно
<section className="bg-[#031E36]">...</section>

<Suspense fallback={<CategoriesSkeleton />}>
  <CategoriesSection />       {/* 'use cache', revalidate 1hr */}
</Suspense>

<Suspense fallback={<TrendingSkeleton />}>
  <TrendingSection />          {/* 'use cache', revalidate 5min */}
</Suspense>

<Suspense fallback={<BlogSkeleton />}>
  <BlogPreviewSection />       {/* 'use cache', revalidate 1hr */}
</Suspense>
```

Hero рендерится статически и немедленно. Секции стримятся независимо, каждая со своим skeleton fallback.

---

## Performance UX

### 'use cache' стратегия (Next.js 16)

| Компонент           | `cacheLife`             | `cacheTag`                     |
| ------------------- | ----------------------- | ------------------------------ |
| `HeroBadge`         | stale 5min / revalidate 30min | `items`, `catalog-stats`  |
| `CategoriesSection` | `'hours'` (1hr)         | `categories`                   |
| `TrendingSection`   | `'catalog'` (5min)      | `items`, `trending`            |
| `BlogPreviewSection`| `'hours'`               | `blog-posts`, `categories`     |

Presigned URLs кэшируются отдельно (45 минут, меньше срока действия URL).

### Perceived performance паттерны

- **Hero мгновенный** — zero data dependencies, рендерится из static shell
- **NavigationProgress** — starts immediately on link click (perceptual feedback)
- **Image fade-in** — `opacity-0 → opacity-100` при onLoad (не резкое появление)
- **GalleryViewer** — `fetchPriority="high"` на главном изображении (LCP сигнал)
- **Optimistic rating** — UI обновляется до ответа сервера
- **Homepage snapshot** — Redis cache `homepage:snapshot` (TTL 10 мин), API отдаёт без DB-запросов на hot path

### Image loading strategy

| Контекст                | Метод               | Приоритет |
| ----------------------- | ------------------- | --------- |
| Gallery главное фото    | `fetchPriority="high"` | LCP       |
| ItemCard превью         | `loading="lazy"` + onLoad fade | lazy |
| RecommendedProducts     | `loading="lazy"`    | lazy      |
| CategoryCard            | Next.js `<Image>` с `fill` | автоматически |

---

## Анимации

Все keyframes определены в `globals.css`. GPU-friendly: только `opacity` и `transform`.

### Keyframes

| Класс                   | Анимация                          | Timing                             |
| ----------------------- | --------------------------------- | ---------------------------------- |
| `.animate-fade-up`      | opacity 0→1, translateY 22px→0    | 0.55s `cubic-bezier(0.16,1,0.3,1)` |
| `.animate-fade-up-1`    | то же, delay 0.1s                 |                                    |
| `.animate-fade-up-2`    | то же, delay 0.2s                 |                                    |
| `.animate-fade-up-3`    | то же, delay 0.3s                 |                                    |
| `.animate-fade-in`      | opacity 0→1                       | 0.4s ease-out                      |
| `.animate-content-appear` | opacity 0→1, translateY 8px→0  | 0.4s `cubic-bezier(0.16,1,0.3,1)` |
| `.skeleton`             | shimmer sweep                     | 1.6s ease-in-out infinite          |
| `.progress-growing`     | width 0%→88%                      | 2.5s `cubic-bezier(0.1,0.6,0.4,1)`|

### Применение на homepage

```
Hero badge  → .animate-fade-up         (0s)
H1          → .animate-fade-up-1       (0.1s)
Subtitle    → .animate-fade-up-2       (0.2s)
Search form → .animate-fade-up-3       (0.3s)
```

Staggered reveal создаёт ощущение "распаковки" страницы без JavaScript.

### Hover-анимации компонентов

| Компонент          | Transform               | Duration  |
| ------------------ | ----------------------- | --------- |
| ItemCard lift      | `-translate-y-1`        | 300ms     |
| ItemCard image     | `scale-105`             | 500ms ease-out |
| RecommendationCard | `-translate-y-0.5`      | 200ms     |
| Rec card image     | `scale-105`             | 500ms ease-out |
| CategoryCard image | `scale-105`             | 300ms     |
| Arrow icon         | `translate-x-0.5`       | 150ms     |

### prefers-reduced-motion

Все CSS animations отключаются через media query в `globals.css`:

```css
@media (prefers-reduced-motion: reduce) {
  .animate-fade-up, .animate-fade-in, .animate-content-appear { animation: none; opacity: 1; }
  .skeleton { animation: none; background: #e8f0f8; }
  .progress-growing { animation: none; width: 60%; }
}
```

---

## Search UX

SearchBar — Server Component (`src/components/ui/SearchBar.tsx`):

- Нативный HTML `<form action="/catalog" method="GET">` — нет JS, работает без hydration
- `focus-within:border-[#9ABCED] focus-within:shadow-md` — визуальный feedback при активации
- Submit кнопка: `bg-[#04335A]` с hover `hover:bg-[#031E36]`
- `defaultValue={initialValue}` — сохраняет текущий поисковый запрос при navigate

На homepage SearchBar встроен в hero section (`shadow-2xl bg-white rounded-2xl`).  
В каталоге — в шапке страницы под заголовком.

> Autocomplete (`/search/suggestions`) подключается к SearchBar на стороне клиента как enhancement — нативный submit работает даже без JS.

---

## Homepage UX

### Структура страницы

```
[Hero — dark navy, статический]
  ├── Gradient orbs (blur, декоративные)
  ├── Badge (live count)
  ├── H1 с gradient text span
  ├── Subtitle
  └── Search form

[CategoriesSection — bg-white]
  ├── Label + H2 + "Все категории" ссылка
  └── CategoryScroller (horizontal)

[TrendingSection — bg-[#f0f5fb]]
  ├── Label "Популярное" + H2 "Trending товары"
  └── 3-col ItemCard grid (top 6 by view_count)

[BlogPreviewSection — bg-white]
  ├── Label "Редакция" + H2 "Статьи и обзоры"
  └── 3-col BlogPostCard grid (latest 3)

[CTA — bg-[#f0f5fb]]
  └── Gradient banner (dark navy → blue) с двумя кнопками
```

### Section naming pattern

Каждая секция кроме hero имеет двухуровневый заголовок:
```
КАТЕГОРИИ          ← uppercase label, text-[#4474A3], tracking-widest
Что ищете?         ← H2 text-3xl font-bold text-[#031E36]
```

### Background чередование

Секции чередуют фоны для визуального разделения: `bg-white` → `bg-[#f0f5fb]` → `bg-white` → `bg-[#f0f5fb]`.

---

## Mobile UX

### Responsive breakpoints

- **Header**: nav скрывается на `md:hidden`, burger появляется
- **Mobile menu**: inline drawer под header (не slide-in overlay) — `border-t border-gray-100`
- **Каталог sidebar**: `w-full` stack над grid на mobile, `lg:w-60 shrink-0` на desktop
- **RecommendedProducts**: горизонтальный scroll (`overflow-x-auto snap-x`) на mobile, grid на `sm+`

### Touch-friendly элементы

- Все tap-targets: минимум `py-2.5 px-4` или `p-2` (≥40px)
- Burger: `p-2 rounded-xl` — явная область клика
- RatingWidget звёзды: `w-6 h-6` интерактивные, `w-5 h-5` статические
- Gallery thumbnails: `w-20 h-16` с `overflow-x-auto pb-1`

---

## Accessibility

### aria-атрибуты в компонентах

| Компонент          | Паттерн                                                  |
| ------------------ | -------------------------------------------------------- |
| NavigationProgress | `aria-hidden="true"` — декоративный элемент             |
| Gradient orbs      | `aria-hidden` — декоративные псевдо-элементы            |
| Skeleton placeholders | `aria-hidden="true"` в ItemCard (`shimmer placeholder`) |
| Burger button      | `aria-label="Открыть меню"`                              |
| RatingWidget stars | `aria-label={`Оценить ${star} из 5`}`                   |
| GalleryViewer      | `alt={title}` на главном, `alt=""` на thumbnails         |

### Semantic HTML

- `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<aside>` — корректная семантика
- Заголовки: строгая иерархия H1 → H2 → H3 без пропусков
- `<form>` с `action`/`method` для SearchBar — работает без JS
- Кнопки (`<button>`) для всего интерактивного, не `<div onClick>`

### Reduced layout shift

Skeleton-компоненты сохраняют точные размеры реального контента:
- `h-60` для card images = реальная высота изображения в ItemCard
- `aspect-video` для gallery skeleton = точный aspect ratio GalleryViewer
- `h-[60px]` для hero search = реальная высота поля ввода

### Focus

- Все кнопки и ссылки фокусируемы по умолчанию (нативные элементы)
- SearchBar: `focus:outline-none` только на `<input>` — focus-ring передаётся контейнеру через `focus-within`
- RatingWidget: `focus:outline-none` на кнопках звёзд (hover-state достаточен визуально, disabled через `cursor-not-allowed`)

---

## Файловая структура UI

```
src/
├── app/
│   ├── globals.css              ← палитра, keyframes, .skeleton, .animate-*
│   ├── layout.tsx               ← Header + NavigationProgress в Suspense + Footer
│   ├── loading.tsx              ← homepage skeleton (hero + 3 sections)
│   ├── page.tsx                 ← homepage (Suspense + 'use cache' sections)
│   ├── catalog/
│   │   ├── loading.tsx          ← sidebar + grid skeleton
│   │   └── [category]/loading.tsx
│   ├── items/[id]/loading.tsx   ← gallery + info + chars + recommended + comments
│   ├── blog/loading.tsx
│   └── blog/[slug]/loading.tsx
├── components/
│   ├── layout/
│   │   ├── Header.tsx           ← sticky, backdrop-blur, mobile drawer
│   │   ├── Footer.tsx
│   │   └── Providers.tsx        ← AuthProvider wrapper
│   └── ui/
│       ├── ItemCard.tsx         ← memo, shimmer image fade-in
│       ├── CategoryCard.tsx     ← presigned image, gradient overlay
│       ├── CategoryScroller.tsx ← horizontal scroll
│       ├── CategoriesFilter.tsx ← sidebar filter
│       ├── SearchBar.tsx        ← Server Component, native form
│       ├── StarRating.tsx       ← static display
│       ├── RatingWidget.tsx     ← interactive + optimistic update
│       ├── GalleryViewer.tsx    ← fetchPriority="high", thumbnail strip
│       ├── CommentsSection.tsx  ← client, local state
│       ├── RecommendedProducts.tsx ← async Server Component, snap scroll mobile
│       ├── RecommendedProductsSkeleton.tsx
│       └── NavigationProgress.tsx ← progress bar, Suspense wrapper
```
