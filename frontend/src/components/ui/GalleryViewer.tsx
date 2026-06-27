'use client'

import { useState } from 'react'
import { GalleryImage } from '@/types'

interface GalleryViewerProps {
  preview: string
  gallery: GalleryImage[]
  title: string
}

export default function GalleryViewer({ preview, gallery, title }: GalleryViewerProps) {
  const images = gallery.length > 0 ? gallery : [{ id: 'preview', item_id: '', image_url: preview }]
  const [activeIdx, setActiveIdx] = useState(0)
  const [imgLoaded, setImgLoaded] = useState(false)

  const handleSelect = (i: number) => {
    if (i === activeIdx) return
    setImgLoaded(false)
    setActiveIdx(i)
  }

  return (
    <div className="space-y-3">
      <div className="relative aspect-video rounded-2xl overflow-hidden bg-gray-100">
        {!imgLoaded && (
          <div className="absolute inset-0 skeleton" aria-hidden="true" />
        )}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={images[activeIdx].image_url}
          alt={title}
          fetchPriority="high"
          decoding="async"
          onLoad={() => setImgLoaded(true)}
          className={`w-full h-full object-cover transition-opacity duration-200 ${imgLoaded ? 'opacity-100' : 'opacity-0'}`}
        />
      </div>
      {images.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {images.map((img, i) => (
            <button
              key={img.id}
              onClick={() => handleSelect(i)}
              className={`w-20 h-16 shrink-0 rounded-lg overflow-hidden bg-gray-100 transition-all ${
                i === activeIdx
                  ? 'ring-2 ring-indigo-600 ring-offset-1'
                  : 'opacity-60 hover:opacity-100'
              }`}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={img.image_url} alt="" loading="lazy" decoding="async" className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
