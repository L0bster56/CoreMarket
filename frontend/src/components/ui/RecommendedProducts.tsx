import Link from 'next/link'
import type { ApiItemDetail, ApiItemListEntry, Category } from '@/types'
import { getRecommendations } from '@/lib/recommendations'
import { serverGetPresignedUrls } from '@/services/storage.server'

// ─── Main component (async Server Component) ──────────────────────────────────

interface Props {
  item: ApiItemDetail
  categories: Category[]
}

export default async function RecommendedProducts({ item, categories }: Props) {
  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]))

  let recs: ApiItemListEntry[] = []
  try {
    recs = await getRecommendations(item, 4)
  } catch {
    return null
  }

  if (recs.length === 0) return null

  const previewKeys = recs
    .map((r) => r.preview_image)
    .filter((k): k is string => Boolean(k))

  const previewUrls =
    previewKeys.length > 0
      ? await serverGetPresignedUrls(previewKeys)
      : ({} as Record<string, string>)

  return (
    <section className="mt-14">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Рекомендуемые товары</h2>
        <p className="mt-1 text-sm text-gray-500">
          Похожие товары, подобранные специально для вас
        </p>
      </div>

      {/*
        Mobile  : horizontal scroll row (flex, fixed card width, snap)
        sm+     : 2-column grid
        lg+     : 4-column grid
      */}
      <div
        className="
          flex gap-4 overflow-x-auto pb-3 -mx-4 px-4 snap-x snap-mandatory scroll-smooth
          sm:grid sm:grid-cols-2 sm:overflow-visible sm:pb-0 sm:mx-0 sm:px-0
          lg:grid-cols-4
        "
      >
        {recs.map((rec) => (
          <RecommendationCard
            key={rec.id}
            item={rec}
            category={categoryMap[rec.category_id]}
            imageUrl={rec.preview_image ? previewUrls[rec.preview_image] : undefined}
          />
        ))}
      </div>
    </section>
  )
}

// ─── Card ─────────────────────────────────────────────────────────────────────

interface CardProps {
  item: ApiItemListEntry
  category?: Category
  imageUrl?: string
}

function RecommendationCard({ item, category, imageUrl }: CardProps) {
  return (
    <Link
      href={`/items/${item.id}`}
      className="
        group flex-none w-72 snap-start
        sm:w-auto
        bg-white rounded-2xl border border-gray-200 overflow-hidden
        hover:shadow-lg hover:border-indigo-200 hover:-translate-y-0.5
        transition-all duration-200
      "
    >
      {/* Thumbnail */}
      <div className="relative h-44 bg-gradient-to-br from-[#eef3f9] to-[#C4D4E6] flex items-center justify-center overflow-hidden">
        {imageUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={imageUrl}
            alt={item.title}
            loading="lazy"
            decoding="async"
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
          />
        ) : (
          <svg
            className="w-10 h-10 text-[#9ABCED] group-hover:scale-110 transition-transform duration-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        )}

        {item.youtube_url && (
          <div className="absolute top-3 right-3">
            <span className="flex items-center gap-1 px-2 py-0.5 bg-red-600 text-white text-xs font-medium rounded-full">
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                <path d="M21.543 6.498C22 8.28 22 12 22 12s0 3.72-.457 5.502c-.254.985-.997 1.76-1.938 2.022C17.896 20 12 20 12 20s-5.893 0-7.605-.476c-.945-.266-1.687-1.04-1.938-2.022C2 15.72 2 12 2 12s0-3.72.457-5.502c.254-.985.997-1.76 1.938-2.022C6.107 4 12 4 12 4s5.896 0 7.605.476c.945.266 1.687 1.04 1.938 2.022z" />
                <path fill="white" d="M10 15.5l6-3.5-6-3.5v7z" />
              </svg>
              YouTube
            </span>
          </div>
        )}
      </div>

      {/* Body */}
      <div className="p-4">
        {category && (
          <span className="text-xs font-semibold text-indigo-600 uppercase tracking-wide">
            {category.name}
          </span>
        )}
        <h3 className="mt-1 text-sm font-semibold text-gray-900 line-clamp-2 leading-snug group-hover:text-indigo-700 transition-colors">
          {item.title}
        </h3>
        <p className="mt-1.5 text-xs text-gray-500 line-clamp-2 leading-relaxed">
          {item.short_description}
        </p>

        <div className="mt-3 flex items-center justify-end">
          <span className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 group-hover:text-indigo-800 transition-colors">
            Подробнее
            <svg
              className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform duration-150"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </div>
      </div>
    </Link>
  )
}
