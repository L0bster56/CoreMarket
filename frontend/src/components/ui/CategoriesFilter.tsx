'use client'

import Link from 'next/link'
import { useState } from 'react'
import type { Category } from '@/types'

const VISIBLE_COUNT = 5

interface Props {
  categories: Category[]
  selectedId?: string
  search?: string
}

export default function CategoriesFilter({ categories, selectedId, search }: Props) {
  const [open, setOpen] = useState(false)

  const visible = categories.slice(0, VISIBLE_COUNT)
  const hidden  = categories.slice(VISIBLE_COUNT)

  const linkCls = (active: boolean) =>
    `block px-3 py-2 rounded-lg text-sm transition-colors ${
      active
        ? 'bg-indigo-50 text-indigo-700 font-semibold'
        : 'text-gray-600 hover:bg-indigo-50/50 hover:text-indigo-600'
    }`

  const hrefFor = (id: string) =>
    `/catalog?category_id=${id}${search ? `&search=${search}` : ''}`

  return (
    <ul className="space-y-0.5">
      <li>
        <Link href="/catalog" className={linkCls(!selectedId)}>
          Все категории
        </Link>
      </li>

      {visible.map((cat) => (
        <li key={cat.id}>
          <Link href={hrefFor(cat.id)} className={linkCls(selectedId === cat.id)}>
            {cat.name}
          </Link>
        </li>
      ))}

      {hidden.length > 0 && (
        <>
          {/* Выпадающий список скрытых категорий */}
          <div
            className="overflow-hidden transition-all duration-300 ease-in-out"
            style={{ maxHeight: open ? hidden.length * 44 + 'px' : '0px' }}
          >
            <ul className="pt-0.5 space-y-0.5">
              {hidden.map((cat) => (
                <li key={cat.id}>
                  <Link href={hrefFor(cat.id)} className={linkCls(selectedId === cat.id)}>
                    {cat.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Кнопка показать / скрыть */}
          <li>
            <button
              onClick={() => setOpen(!open)}
              className="flex w-full items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-indigo-600 hover:bg-indigo-50/50 transition-colors"
            >
              <svg
                className={`w-4 h-4 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              {open ? 'Скрыть' : `Ещё ${hidden.length}`}
            </button>
          </li>
        </>
      )}
    </ul>
  )
}
