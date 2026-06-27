'use client'

import { memo, useState } from 'react'
import Link from 'next/link'
import { Item } from '@/types'
import StarRating from './StarRating'

interface ItemCardProps {
  item: Item
  imageUrl?: string
}

const ItemCard = memo(function ItemCard({ item, imageUrl }: ItemCardProps) {
  const [imgLoaded, setImgLoaded] = useState(false)

  return (
    <Link
      href={`/items/${item.id}`}
      className="group block bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-gray-100/80"
    >
      {/* Image */}
      <div className="relative h-60 bg-gradient-to-br from-[#eef3f9] to-[#C4D4E6] overflow-hidden">
        {imageUrl ? (
          <>
            {/* Shimmer placeholder shown until image loads */}
            {!imgLoaded && (
              <div className="absolute inset-0 skeleton" aria-hidden="true" />
            )}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt={item.title}
              loading="lazy"
              decoding="async"
              onLoad={() => setImgLoaded(true)}
              className={`w-full h-full object-cover group-hover:scale-105 transition-all duration-500 ease-out ${
                imgLoaded ? 'opacity-100' : 'opacity-0'
              }`}
            />
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="w-16 h-16 rounded-2xl bg-white/60 flex items-center justify-center">
              <svg className="w-8 h-8 text-[#9ABCED]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        )}

        {/* Gradient overlay */}
        <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />

        {/* Category badge */}
        {item.category && (
          <div className="absolute top-3 left-3">
            <span className="px-2.5 py-1 bg-white/90 backdrop-blur-sm text-[#04335A] text-xs font-semibold rounded-full shadow-sm">
              {item.category.name}
            </span>
          </div>
        )}

        {/* YouTube badge */}
        {item.youtube_url && (
          <div className="absolute top-3 right-3">
            <span className="flex items-center gap-1 px-2 py-0.5 bg-red-600 text-white text-xs font-medium rounded-full shadow-sm">
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                <path d="M21.543 6.498C22 8.28 22 12 22 12s0 3.72-.457 5.502c-.254.985-.997 1.76-1.938 2.022C17.896 20 12 20 12 20s-5.893 0-7.605-.476c-.945-.266-1.687-1.04-1.938-2.022C2 15.72 2 12 2 12s0-3.72.457-5.502c.254-.985.997-1.76 1.938-2.022C6.107 4 12 4 12 4s5.896 0 7.605.476c.945.266 1.687 1.04 1.938 2.022z"/>
                <path fill="white" d="M10 15.5l6-3.5-6-3.5v7z"/>
              </svg>
              Video
            </span>
          </div>
        )}

        {/* Tag pills — bottom overlay */}
        {item.tags && item.tags.length > 0 && (
          <div className="absolute bottom-3 left-3 flex gap-1.5">
            {item.tags.slice(0, 2).map((tag) => (
              <span
                key={tag.id}
                className="px-2.5 py-0.5 bg-[#04335A]/80 backdrop-blur-sm text-white text-xs font-medium rounded-full"
              >
                {tag.name}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5">
        <h3 className="font-bold text-[#031E36] text-base leading-snug line-clamp-2 group-hover:text-[#04335A] transition-colors mb-2">
          {item.title}
        </h3>
        <p className="text-sm text-gray-500 line-clamp-2 leading-relaxed mb-4">
          {item.short_description}
        </p>
        <div className="flex items-center justify-between pt-3 border-t border-gray-50">
          {item.avg_rating !== undefined ? (
            <StarRating score={item.avg_rating} count={item.rating_count} size="sm" />
          ) : (
            <span />
          )}
          {item.view_count !== undefined && (
            <span className="flex items-center gap-1 text-xs text-gray-400">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {item.view_count.toLocaleString('ru-RU')}
            </span>
          )}
        </div>
      </div>
    </Link>
  )
})

export default ItemCard
