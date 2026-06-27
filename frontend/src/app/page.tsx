import type { Metadata } from 'next'
import { Suspense } from 'react'
import { cacheLife, cacheTag } from 'next/cache'
import Link from 'next/link'
import { serverGet } from '@/lib/server-fetch'
import { serverGetPresignedUrls } from '@/services/storage.server'
import type { Category, ApiItemListResponse, Item, BlogListResponse } from '@/types'
import ItemCard from '@/components/ui/ItemCard'
import BlogPostCard from '@/components/blog/BlogPostCard'
import CategoryScroller from '@/components/ui/CategoryScroller'

export const metadata: Metadata = {
  title: { absolute: 'CoreMarket — Каталог товаров' },
  description:
    'Каталог товаров с обзорами, характеристиками и рейтингами. Сравнивайте и выбирайте лучшее.',
  openGraph: {
    title: 'CoreMarket — Каталог товаров',
    description: 'Каталог товаров с обзорами, характеристиками и рейтингами.',
    url: '/',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'CoreMarket — Каталог товаров',
    description: 'Каталог товаров с обзорами, характеристиками и рейтингами.',
  },
}

const websiteJsonLd = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'CoreMarket',
  url: process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000',
  potentialAction: {
    '@type': 'SearchAction',
    target: {
      '@type': 'EntryPoint',
      urlTemplate: `${process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000'}/catalog?search={search_term_string}`,
    },
    'query-input': 'required name=search_term_string',
  },
}

const ArrowRight = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
  </svg>
)

// ─── Cached: Hero badge count (revalidates every 30min) ─────────────────────

async function HeroBadge() {
  'use cache'
  cacheLife({ stale: 300, revalidate: 1800, expire: 86400 })
  cacheTag('items', 'catalog-stats')

  const resp = await serverGet<{ total: number }>('/items?limit=1&is_published=true', 1800)
  const total = resp.total

  return (
    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 backdrop-blur-sm border border-white/15 text-white/80 text-sm">
      <span className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
      {total > 0 ? `${total}+ товаров в каталоге` : 'Актуальный каталог'}
    </div>
  )
}

// ─── Cached: Categories section (revalidates every 1hr) ─────────────────────

async function CategoriesSection() {
  'use cache'
  cacheLife('hours')
  cacheTag('categories')

  const categories = await serverGet<Category[]>('/categories', 3600)

  if (categories.length === 0) return null

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between mb-8">
          <div>
            <p className="text-[#4474A3] font-semibold text-xs tracking-widest uppercase mb-1.5">
              Категории
            </p>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#031E36]">Что ищете?</h2>
          </div>
          <Link
            href="/catalog"
            className="flex items-center gap-1 text-sm text-[#4474A3] hover:text-[#04335A] font-medium transition-colors"
          >
            Все категории
            <ArrowRight />
          </Link>
        </div>
        <CategoryScroller categories={categories} />
      </div>
    </section>
  )
}

// ─── Cached: Trending products (revalidates every 5min) ──────────────────────
// Presigned URLs come from 'use cache: remote' inside serverGetPresignedUrls.

async function TrendingSection() {
  'use cache'
  cacheLife('catalog')
  cacheTag('items', 'trending')

  const [categories, itemsResp] = await Promise.all([
    serverGet<Category[]>('/categories', 300),
    serverGet<ApiItemListResponse>('/items?limit=20&is_published=true', 300),
  ])

  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]))

  const featuredItems: Item[] = itemsResp.items
    .slice()
    .sort((a, b) => b.view_count - a.view_count)
    .slice(0, 6)
    .map((e) => ({
      ...e,
      youtube_url: e.youtube_url ?? undefined,
      preview_image: e.preview_image ?? undefined,
      category: categoryMap[e.category_id],
    }))

  if (featuredItems.length === 0) return null

  const previewKeys = featuredItems
    .map((item) => item.preview_image)
    .filter((k): k is string => Boolean(k))

  const previewUrls = previewKeys.length > 0
    ? await serverGetPresignedUrls(previewKeys)
    : {} as Record<string, string>

  return (
    <section className="py-16 bg-[#f0f5fb]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between mb-8">
          <div>
            <p className="text-[#4474A3] font-semibold text-xs tracking-widest uppercase mb-1.5">
              Популярное
            </p>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#031E36]">Trending товары</h2>
          </div>
          <Link
            href="/catalog"
            className="flex items-center gap-1 text-sm text-[#4474A3] hover:text-[#04335A] font-medium transition-colors"
          >
            Смотреть все
            <ArrowRight />
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {featuredItems.map((item) => (
            <ItemCard
              key={item.id}
              item={item}
              imageUrl={item.preview_image ? previewUrls[item.preview_image] : undefined}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── Cached: Blog preview (revalidates every 1hr) ───────────────────────────

async function BlogPreviewSection() {
  'use cache'
  cacheLife('hours')
  cacheTag('blog-posts', 'categories')

  const [categories, blogResp] = await Promise.all([
    serverGet<Category[]>('/categories', 3600),
    serverGet<BlogListResponse>('/blog/posts?post_status=published&limit=3', 3600)
      .catch((): BlogListResponse => ({ items: [], total: 0 })),
  ])

  if (blogResp.items.length === 0) return null

  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]))

  const coverKeys = blogResp.items
    .map((p) => p.cover_image_url)
    .filter((k): k is string => Boolean(k))
  const coverUrls = coverKeys.length > 0
    ? await serverGetPresignedUrls(coverKeys)
    : {} as Record<string, string>

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between mb-8">
          <div>
            <p className="text-[#4474A3] font-semibold text-xs tracking-widest uppercase mb-1.5">
              Редакция
            </p>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#031E36]">Статьи и обзоры</h2>
          </div>
          <Link
            href="/blog"
            className="flex items-center gap-1 text-sm text-[#4474A3] hover:text-[#04335A] font-medium transition-colors"
          >
            Все статьи
            <ArrowRight />
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {blogResp.items.map((post) => (
            <BlogPostCard
              key={post.id}
              post={post}
              categoryName={
                post.category_id ? categoryMap[post.category_id]?.name : undefined
              }
              coverImageUrl={post.cover_image_url ? coverUrls[post.cover_image_url] : undefined}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── Skeletons for Suspense fallbacks ───────────────────────────────────────

function S({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-full ${className}`} />
}

function SBox({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-2xl ${className}`} />
}

function CategoriesSkeleton() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between mb-8">
          <div className="space-y-2">
            <S className="h-3 w-20" />
            <S className="h-7 w-36" />
          </div>
          <S className="h-3 w-24" />
        </div>
        <div className="flex gap-3 overflow-hidden">
          {Array.from({ length: 7 }).map((_, i) => (
            <SBox key={i} className="w-36 h-24 shrink-0" />
          ))}
        </div>
      </div>
    </section>
  )
}

function TrendingSkeleton() {
  return (
    <section className="py-16 bg-[#f0f5fb]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between mb-8">
          <div className="space-y-2">
            <S className="h-3 w-24" />
            <S className="h-7 w-44" />
          </div>
          <S className="h-3 w-20" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-3xl overflow-hidden border border-gray-100/80 shadow-sm">
              <SBox className="h-60 !rounded-none" />
              <div className="p-5 space-y-3">
                <S className="h-4 w-4/5" />
                <S className="h-3 w-full" />
                <S className="h-3 w-3/4" />
                <div className="pt-3 border-t border-gray-50 flex justify-between">
                  <S className="h-3 w-24" />
                  <S className="h-3 w-10" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function BlogSkeleton() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between mb-8">
          <div className="space-y-2">
            <S className="h-3 w-16" />
            <S className="h-7 w-40" />
          </div>
          <S className="h-3 w-20" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl overflow-hidden border border-gray-100 shadow-sm">
              <SBox className="h-44 !rounded-none" />
              <div className="p-5 space-y-3">
                <S className="h-3 w-20" />
                <S className="h-5 w-4/5" />
                <S className="h-3 w-full" />
                <S className="h-3 w-3/4" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── Page ────────────────────────────────────────────────────────────────────
// Hero is fully static (no data dependencies) — renders in the static shell
// instantly. Cached sub-components are prerendered at build/revalidation time.
// Suspense boundaries provide skeleton fallbacks on first cold render.

export default function HomePage() {
  return (
    <div>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd) }}
      />

      {/* ─── HERO (static shell) ─── */}
      <section className="relative overflow-hidden bg-[#031E36]">
        <div
          aria-hidden
          className="absolute top-0 left-1/4 w-[700px] h-[700px] rounded-full bg-[#04335A] blur-[140px] opacity-80 -translate-x-1/2 -translate-y-1/3 pointer-events-none"
        />
        <div
          aria-hidden
          className="absolute bottom-0 right-0 w-80 h-80 rounded-full bg-[#4474A3] blur-[100px] opacity-20 translate-x-1/3 translate-y-1/3 pointer-events-none"
        />
        <div
          aria-hidden
          className="absolute top-1/2 left-0 w-64 h-64 rounded-full bg-[#9ABCED] blur-[100px] opacity-10 -translate-x-1/2 pointer-events-none"
        />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-36 text-center">

          {/* Badge — cached catalog count */}
          <div className="flex justify-center mb-8 animate-fade-up">
            <Suspense
              fallback={
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 border border-white/15 text-white/80 text-sm">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
                  Актуальный каталог
                </div>
              }
            >
              <HeroBadge />
            </Suspense>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-5 animate-fade-up-1">
            Найдите идеальный
            <br />
            <span className="bg-gradient-to-r from-[#9ABCED] via-[#C4D4E6] to-[#9ABCED] bg-clip-text text-transparent">
              товар для вас
            </span>
          </h1>

          <p className="text-lg text-white/60 max-w-lg mx-auto mb-10 animate-fade-up-2">
            Каталог с обзорами, характеристиками и рейтингами. Сравнивайте и выбирайте лучшее.
          </p>

          <div className="max-w-2xl mx-auto animate-fade-up-3">
            <form action="/catalog" method="GET">
              <div className="flex gap-2 p-2 bg-white rounded-2xl shadow-2xl">
                <div className="relative flex-1">
                  <svg
                    className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <input
                    type="text"
                    name="search"
                    placeholder="Поиск смартфонов, ноутбуков, техники..."
                    className="w-full pl-12 pr-4 py-3.5 text-gray-900 bg-transparent text-base focus:outline-none placeholder:text-gray-400"
                  />
                </div>
                <button
                  type="submit"
                  className="px-6 py-3.5 bg-[#04335A] hover:bg-[#031E36] text-white font-semibold rounded-xl transition-colors text-sm shrink-0"
                >
                  Найти
                </button>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* ─── CATEGORIES (cached 1hr, streams on cold miss) ─── */}
      <Suspense fallback={<CategoriesSkeleton />}>
        <CategoriesSection />
      </Suspense>

      {/* ─── TRENDING PRODUCTS (cached 5min, streams on cold miss) ─── */}
      <Suspense fallback={<TrendingSkeleton />}>
        <TrendingSection />
      </Suspense>

      {/* ─── BLOG PREVIEW (cached 1hr, streams on cold miss) ─── */}
      <Suspense fallback={<BlogSkeleton />}>
        <BlogPreviewSection />
      </Suspense>

      {/* ─── CTA (static shell) ─── */}
      <section className="py-16 bg-[#f0f5fb]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#031E36] via-[#04335A] to-[#4474A3] px-8 py-16 text-center">
            <div
              aria-hidden
              className="absolute top-0 right-1/4 w-64 h-64 rounded-full bg-[#9ABCED] blur-3xl opacity-15 pointer-events-none"
            />
            <div
              aria-hidden
              className="absolute bottom-0 left-1/4 w-48 h-48 rounded-full bg-white blur-3xl opacity-5 pointer-events-none"
            />
            <div className="relative">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Найдите всё что нужно
              </h2>
              <p className="text-white/60 max-w-md mx-auto mb-8 text-base leading-relaxed">
                Тысячи товаров с подробными обзорами, характеристиками и рейтингами пользователей.
              </p>
              <div className="flex gap-3 justify-center flex-wrap">
                <Link
                  href="/catalog"
                  className="px-8 py-3.5 bg-white text-[#031E36] font-semibold rounded-xl hover:bg-[#eef3f9] transition-colors text-sm"
                >
                  Перейти в каталог
                </Link>
                <Link
                  href="/blog"
                  className="px-8 py-3.5 bg-white/10 text-white font-semibold rounded-xl border border-white/20 hover:bg-white/20 transition-colors text-sm"
                >
                  Читать блог
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
