'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { Category } from '@/types'
import { getCachedOrFetch } from '@/lib/presigned-cache'

interface CategoryCardProps {
  category: Category
  itemCount?: number
}

export default function CategoryCard({ category, itemCount }: CategoryCardProps) {
  const [resolvedImage, setResolvedImage] = useState<string | undefined>(undefined)

  useEffect(() => {
    if (!category.image_url) return
    getCachedOrFetch([category.image_url])
      .then((urls) => setResolvedImage(urls[category.image_url!]))
      .catch(() => {})
  }, [category.image_url])

  return (
    <Link
      href={`/catalog/${category.slug}`}
      className="group relative overflow-hidden rounded-2xl bg-gray-900 aspect-video flex items-end hover:ring-2 hover:ring-indigo-500 transition-all duration-200"
    >
      {resolvedImage && (
        <Image
          src={resolvedImage}
          alt={category.name}
          fill
          className="object-cover opacity-60 group-hover:opacity-50 group-hover:scale-105 transition-all duration-300"
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
        />
      )}
      <div className="relative z-10 p-5 w-full bg-gradient-to-t from-black/80 to-transparent">
        <h3 className="text-white font-bold text-lg leading-tight">{category.name}</h3>
        {itemCount !== undefined && (
          <p className="text-gray-300 text-sm mt-0.5">{itemCount} объектов</p>
        )}
      </div>
    </Link>
  )
}
