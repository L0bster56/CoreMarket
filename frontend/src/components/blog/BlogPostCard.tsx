import Link from 'next/link'
import type { BlogPostListEntry } from '@/types'

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

interface BlogPostCardProps {
  post: BlogPostListEntry
  categoryName?: string
  coverImageUrl?: string
}

export default function BlogPostCard({ post, categoryName, coverImageUrl }: BlogPostCardProps) {
  const imageSrc = coverImageUrl ?? undefined

  return (
    <Link
      href={`/blog/${post.slug}`}
      className="group flex flex-col bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-gray-100/80"
    >
      {/* Cover */}
      <div className="relative h-52 bg-gradient-to-br from-[#eef3f9] to-[#C4D4E6] overflow-hidden shrink-0">
        {imageSrc ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={imageSrc}
            alt={post.title}
            loading="lazy"
            decoding="async"
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="w-16 h-16 rounded-2xl bg-white/60 flex items-center justify-center">
              <svg className="w-8 h-8 text-[#9ABCED]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 12h6m-6-4h6" />
              </svg>
            </div>
          </div>
        )}

        {/* Gradient overlay */}
        <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-black/30 to-transparent pointer-events-none" />

        {/* Category badge */}
        {categoryName && (
          <div className="absolute top-3 left-3">
            <span className="px-2.5 py-1 bg-white/90 backdrop-blur-sm text-[#04335A] text-xs font-semibold rounded-full shadow-sm">
              {categoryName}
            </span>
          </div>
        )}

        {/* Date */}
        <div className="absolute bottom-3 right-3">
          <span className="text-xs text-white/80 font-medium drop-shadow">
            {formatDate(post.created_at)}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-col flex-1 p-5">
        <h3 className="text-base font-bold text-[#031E36] line-clamp-2 group-hover:text-[#04335A] transition-colors mb-2">
          {post.title}
        </h3>
        {post.short_description && (
          <p className="text-sm text-gray-500 line-clamp-3 flex-1 leading-relaxed">
            {post.short_description}
          </p>
        )}
        <div className="mt-4 flex items-center gap-1.5 text-[#4474A3] text-xs font-semibold">
          <span>Читать статью</span>
          <svg
            className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform duration-200"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </div>
      </div>
    </Link>
  )
}
