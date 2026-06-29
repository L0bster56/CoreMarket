import { Suspense } from 'react'
import { cacheLife, cacheTag } from 'next/cache'
import { serverGet } from '@/lib/server-fetch'
import { serverGetPresignedUrls } from '@/services/storage.server'
import type { Category, Tag, ApiItemListResponse, Item } from '@/types'
import ItemCard from '@/components/ui/ItemCard'
import SearchBar from '@/components/ui/SearchBar'
import CategoriesFilter from '@/components/ui/CategoriesFilter'
import Link from 'next/link'

interface SearchParams {
  search?: string
  category_id?: string
  tag?: string
  min_rating?: string
}

interface PageProps {
  searchParams: Promise<SearchParams>
}

export const metadata = { title: 'Каталог' }

// ─── Cached sidebar data (stable key — no filter props) ──────────────────────

async function fetchSidebarData(): Promise<{ categories: Category[]; tags: Tag[] }> {
  'use cache'
  cacheLife('hours')
  cacheTag('categories', 'tags')

  const [categories, tags] = await Promise.all([
    serverGet<Category[]>('/categories', 3600),
    serverGet<Tag[]>('/tags', 3600),
  ])
  return { categories, tags }
}

// ─── Sidebar renderer (per-request, no cache — depends on filter props) ───────

async function CatalogSidebar({
  selectedCategoryId,
  selectedTag,
  search,
  minRating,
}: {
  selectedCategoryId?: string
  selectedTag?: string
  search?: string
  minRating?: number
}) {
  const { categories, tags } = await fetchSidebarData()

  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]))
  const activeCategory = selectedCategoryId ? categoryMap[selectedCategoryId] : undefined

  return (
    <>
      {/* Активные фильтры — rendered from props, no fetch needed */}
      {activeCategory && (
        <div className="mb-6 flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#04335A] text-white text-xs font-medium">
            {activeCategory.name}
            <Link
              href={`/catalog?${new URLSearchParams({
                ...(search ? { search } : {}),
                ...(selectedTag ? { tag: selectedTag } : {}),
                ...(minRating ? { min_rating: String(minRating) } : {}),
              }).toString()}`}
              className="ml-0.5 hover:opacity-70 transition-opacity"
              aria-label="Убрать категорию"
            >
              ×
            </Link>
          </span>
        </div>
      )}

      {/* Категории */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
        <h3 className="text-xs font-bold text-[#04335A] uppercase tracking-widest mb-3">
          Категории
        </h3>
        <CategoriesFilter
          categories={categories}
          selectedId={selectedCategoryId}
          search={search}
        />
      </div>

      {/* Рейтинг */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mt-4">
        <h3 className="text-xs font-bold text-[#04335A] uppercase tracking-widest mb-3">
          Рейтинг
        </h3>
        <ul className="space-y-0.5">
          <li>
            <Link
              href={`/catalog${search ? `?search=${search}` : ''}${selectedCategoryId ? `${search ? '&' : '?'}category_id=${selectedCategoryId}` : ''}`}
              className={`block px-3 py-2 rounded-xl text-sm transition-colors ${
                !minRating
                  ? 'bg-[#eef3f9] text-[#04335A] font-semibold'
                  : 'text-gray-600 hover:bg-[#eef3f9]/50 hover:text-[#04335A]'
              }`}
            >
              Любой рейтинг
            </Link>
          </li>
          {[4, 3, 2].map((r) => (
            <li key={r}>
              <Link
                href={`/catalog?min_rating=${r}${search ? `&search=${search}` : ''}${selectedCategoryId ? `&category_id=${selectedCategoryId}` : ''}`}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm transition-colors ${
                  minRating === r
                    ? 'bg-[#eef3f9] text-[#04335A] font-semibold'
                    : 'text-gray-600 hover:bg-[#eef3f9]/50 hover:text-[#04335A]'
                }`}
              >
                <span className="text-amber-400">{'★'.repeat(r)}</span>
                <span className="text-amber-200">{'★'.repeat(5 - r)}</span>
                <span className="ml-1">и выше</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>

      {/* Теги */}
      {tags.length > 0 && (
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mt-4">
          <h3 className="text-xs font-bold text-[#04335A] uppercase tracking-widest mb-3">
            Теги
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {tags.map((t) => (
              <Link
                key={t.id}
                href={`/catalog?tag=${t.slug}${search ? `&search=${search}` : ''}`}
                className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                  selectedTag === t.slug
                    ? 'bg-[#04335A] text-white'
                    : 'bg-[#eef3f9] text-[#4474A3] hover:bg-[#C4D4E6] hover:text-[#04335A]'
                }`}
              >
                {t.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

// ─── Dynamic: items grid (depends on searchParams) ───────────────────────────

async function ItemsGrid({ params }: { params: SearchParams }) {
  const { search, category_id, tag } = params
  const minRating = params.min_rating ? Number(params.min_rating) : undefined

  const qs = new URLSearchParams()
  qs.set('is_published', 'true')
  if (search) qs.set('search', search)
  if (category_id) qs.set('category_id', category_id)
  if (tag) qs.set('tag', tag)
  if (minRating !== undefined) qs.set('min_rating', String(minRating))

  const [categories, itemsResp] = await Promise.all([
    serverGet<Category[]>('/categories', 3600),
    serverGet<ApiItemListResponse>(`/items?${qs.toString()}`, false),
  ])

  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]))

  const items: Item[] = itemsResp.items.map((e) => ({
    ...e,
    youtube_url: e.youtube_url ?? undefined,
    preview_image: e.preview_image ?? undefined,
    category: categoryMap[e.category_id],
  }))

  const previewKeys = items
    .map((item) => item.preview_image)
    .filter((k): k is string => Boolean(k))

  const previewUrls = previewKeys.length > 0
    ? await serverGetPresignedUrls(previewKeys)
    : {} as Record<string, string>

  const hasActiveFilters = !!(search || category_id || tag || minRating)

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="w-16 h-16 rounded-2xl bg-[#eef3f9] flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-[#9ABCED]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="font-semibold text-[#031E36] mb-1">Ничего не найдено</p>
        <p className="text-sm text-gray-500 mb-4">
          Попробуйте изменить фильтры или поисковый запрос
        </p>
        {hasActiveFilters && (
          <Link
            href="/catalog"
            className="px-5 py-2.5 bg-[#04335A] text-white text-sm font-semibold rounded-xl hover:bg-[#031E36] transition-colors"
          >
            Сбросить фильтры
          </Link>
        )}
      </div>
    )
  }

  return (
    <>
      <p className="text-sm text-gray-500 mb-4">
        Найдено: <span className="font-semibold text-[#031E36]">{itemsResp.total}</span>
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
        {items.map((item) => (
          <ItemCard
            key={item.id}
            item={item}
            imageUrl={item.preview_image ? previewUrls[item.preview_image] : undefined}
          />
        ))}
      </div>
    </>
  )
}

function ItemsGridSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
      {Array.from({ length: 9 }).map((_, i) => (
        <div key={i} className="bg-gray-100 rounded-2xl h-64 animate-pulse" />
      ))}
    </div>
  )
}

function SidebarSkeleton() {
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
        <div className="h-4 w-24 bg-gray-100 rounded mb-3 animate-pulse" />
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-8 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    </div>
  )
}

// ─── Page ────────────────────────────────────────────────────────────────────
// Sidebar (categories/tags) is prerendered and cached for 1hr.
// Items grid is dynamic (searchParams) and streams at request time.

export default async function CatalogPage({ searchParams }: PageProps) {
  const params = await searchParams
  const { search, category_id, tag, min_rating } = params
  const minRating = min_rating ? Number(min_rating) : undefined

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[#031E36] mb-1">Каталог</h1>
      </div>

      {/* Search */}
      <SearchBar
        placeholder="Поиск по каталогу..."
        className="mb-6 max-w-2xl"
        initialValue={search ?? ''}
      />

      {/* Active filter chips */}
      {(search || tag || minRating) && (
        <div className="flex flex-wrap gap-2 mb-6">
          {search && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#04335A] text-white text-xs font-medium">
              Поиск: «{search}»
              <Link
                href={`/catalog?${new URLSearchParams({
                  ...(category_id ? { category_id } : {}),
                  ...(tag ? { tag } : {}),
                  ...(minRating ? { min_rating: String(minRating) } : {}),
                }).toString()}`}
                className="ml-0.5 hover:opacity-70 transition-opacity"
                aria-label="Убрать поиск"
              >
                ×
              </Link>
            </span>
          )}
          {tag && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#04335A] text-white text-xs font-medium">
              #{tag}
              <Link
                href={`/catalog?${new URLSearchParams({
                  ...(search ? { search } : {}),
                  ...(category_id ? { category_id } : {}),
                  ...(minRating ? { min_rating: String(minRating) } : {}),
                }).toString()}`}
                className="ml-0.5 hover:opacity-70 transition-opacity"
                aria-label="Убрать тег"
              >
                ×
              </Link>
            </span>
          )}
          {minRating && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#04335A] text-white text-xs font-medium">
              Рейтинг {minRating}★+
              <Link
                href={`/catalog?${new URLSearchParams({
                  ...(search ? { search } : {}),
                  ...(category_id ? { category_id } : {}),
                  ...(tag ? { tag } : {}),
                }).toString()}`}
                className="ml-0.5 hover:opacity-70 transition-opacity"
                aria-label="Убрать рейтинг"
              >
                ×
              </Link>
            </span>
          )}
          <Link
            href="/catalog"
            className="px-3 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium hover:bg-gray-200 transition-colors"
          >
            Сбросить всё
          </Link>
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-8">
        {/* ── Sidebar ── */}
        <aside className="w-full lg:w-60 shrink-0">
          <Suspense fallback={<SidebarSkeleton />}>
            <CatalogSidebar
              selectedCategoryId={category_id}
              selectedTag={tag}
              search={search}
              minRating={minRating}
            />
          </Suspense>
        </aside>

        {/* ── Items grid ── */}
        <div className="flex-1 min-w-0">
          <Suspense fallback={<ItemsGridSkeleton />}>
            <ItemsGrid params={params} />
          </Suspense>
        </div>
      </div>
    </div>
  )
}
