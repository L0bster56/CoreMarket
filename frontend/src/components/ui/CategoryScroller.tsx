'use client'

import { useRef, useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import type { Category } from '@/types'

const BG_VARIANTS = [
  'from-blue-50 to-[#C4D4E6]',
  'from-sky-50 to-[#C4D4E6]',
  'from-indigo-50 to-[#C4D4E6]',
  'from-slate-50 to-[#C4D4E6]',
]

interface Props {
  categories: Category[]
}

export default function CategoryScroller({ categories }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [canLeft, setCanLeft] = useState(false)
  const [canRight, setCanRight] = useState(false)

  const sync = useCallback(() => {
    const el = scrollRef.current
    if (!el) return
    setCanLeft(el.scrollLeft > 4)
    setCanRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 4)
  }, [])

  useEffect(() => {
    sync()
    const el = scrollRef.current
    if (!el) return
    el.addEventListener('scroll', sync, { passive: true })
    const ro = new ResizeObserver(sync)
    ro.observe(el)
    return () => {
      el.removeEventListener('scroll', sync)
      ro.disconnect()
    }
  }, [sync])

  const scroll = (dir: 'left' | 'right') => {
    scrollRef.current?.scrollBy({ left: dir === 'left' ? -320 : 320, behavior: 'smooth' })
  }

  return (
    <div className="relative group/scroller">

      {/* Left fade + arrow */}
      <div
        className={`absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-white to-transparent z-10 pointer-events-none transition-opacity duration-200 ${canLeft ? 'opacity-100' : 'opacity-0'}`}
      />
      <button
        onClick={() => scroll('left')}
        aria-label="Прокрутить влево"
        className={`absolute left-2 top-1/2 -translate-y-1/2 z-20 w-9 h-9 rounded-full bg-white shadow-md border border-gray-100 flex items-center justify-center text-[#04335A] hover:bg-[#eef3f9] hover:shadow-lg transition-all duration-200 ${canLeft ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      {/* Scroll container */}
      <div
        ref={scrollRef}
        className="flex gap-3 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden scroll-smooth px-0.5 py-1"
      >
        {categories.map((cat, i) => (
          <Link
            key={cat.id}
            href={`/catalog/${cat.slug}`}
            className={`group shrink-0 w-40 rounded-2xl bg-gradient-to-br ${BG_VARIANTS[i % BG_VARIANTS.length]} p-5 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 flex flex-col gap-3`}
          >
            <div className="w-10 h-10 rounded-xl bg-[#04335A] flex items-center justify-center shadow-sm group-hover:bg-[#031E36] transition-colors shrink-0">
              <span className="text-white font-bold text-base select-none">
                {cat.name[0]}
              </span>
            </div>
            <h3 className="font-semibold text-[#031E36] text-sm leading-tight line-clamp-2">
              {cat.name}
            </h3>
          </Link>
        ))}
      </div>

      {/* Right fade + arrow */}
      <div
        className={`absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-white to-transparent z-10 pointer-events-none transition-opacity duration-200 ${canRight ? 'opacity-100' : 'opacity-0'}`}
      />
      <button
        onClick={() => scroll('right')}
        aria-label="Прокрутить вправо"
        className={`absolute right-2 top-1/2 -translate-y-1/2 z-20 w-9 h-9 rounded-full bg-white shadow-md border border-gray-100 flex items-center justify-center text-[#04335A] hover:bg-[#eef3f9] hover:shadow-lg transition-all duration-200 ${canRight ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
        </svg>
      </button>

    </div>
  )
}
