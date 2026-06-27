'use client'

import Link from 'next/link'
import Image from 'next/image'
import { usePathname, useRouter } from 'next/navigation'
import { useState, useMemo, useCallback } from 'react'
import { useAuth } from '@/lib/auth-context'

const baseNav = [
  { href: '/', label: 'Главная' },
  { href: '/catalog', label: 'Каталог' },
  { href: '/blog', label: 'Блог' },
]

export default function Header() {
  const pathname = usePathname()
  const router = useRouter()
  const [menuOpen, setMenuOpen] = useState(false)
  const { user, logout } = useAuth()

  const nav = useMemo(
    () => user?.role === 'admin' ? [...baseNav, { href: '/admin', label: 'Админ' }] : baseNav,
    [user?.role],
  )

  const handleLogout = useCallback(async () => {
    await logout()
    router.push('/')
    setMenuOpen(false)
  }, [logout, router])

  return (
    <header className="sticky top-0 z-50 bg-white/85 backdrop-blur-xl border-b border-gray-200/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 shrink-0">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#04335A] to-[#4474A3] flex items-center justify-center shadow-sm">
              <span className="text-white font-bold text-xs tracking-tight">CM</span>
            </div>
            <span className="font-bold text-lg text-[#031E36] tracking-tight">CoreMarket</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-0.5">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                  pathname === item.href
                    ? 'bg-[#eef3f9] text-[#04335A] font-semibold'
                    : 'text-gray-600 hover:text-[#031E36] hover:bg-gray-50/80'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Desktop auth */}
          <div className="hidden md:flex items-center gap-2">
            {user ? (
              <>
                <Link
                  href="/profile"
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  {user.avatar_url ? (
                    <Image
                      src={user.avatar_url}
                      alt={user.username}
                      width={28}
                      height={28}
                      className="rounded-full"
                    />
                  ) : (
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#04335A] to-[#4474A3] flex items-center justify-center">
                      <span className="text-xs font-bold text-white">
                        {user.username[0].toUpperCase()}
                      </span>
                    </div>
                  )}
                  <span className="text-sm font-medium text-gray-700">{user.username}</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="px-3 py-1.5 text-sm font-medium text-gray-500 hover:text-red-500 transition-colors"
                >
                  Выйти
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-[#031E36] transition-colors"
                >
                  Войти
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 bg-[#04335A] hover:bg-[#031E36] text-white text-sm font-semibold rounded-xl transition-colors shadow-sm"
                >
                  Регистрация
                </Link>
              </>
            )}
          </div>

          {/* Mobile burger */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden p-2 rounded-xl text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label="Открыть меню"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden py-3 border-t border-gray-100 space-y-0.5">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMenuOpen(false)}
                className={`block px-4 py-2.5 text-sm font-medium rounded-xl transition-colors ${
                  pathname === item.href
                    ? 'bg-[#eef3f9] text-[#04335A]'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                {item.label}
              </Link>
            ))}
            <div className="pt-2 border-t border-gray-100 mt-2 flex flex-col gap-1 px-2">
              {user ? (
                <>
                  <Link
                    href="/profile"
                    onClick={() => setMenuOpen(false)}
                    className="flex items-center gap-2.5 px-2 py-2.5 text-sm font-medium text-gray-700 rounded-xl hover:bg-gray-50"
                  >
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#04335A] to-[#4474A3] flex items-center justify-center shrink-0">
                      <span className="text-xs font-bold text-white">{user.username[0].toUpperCase()}</span>
                    </div>
                    {user.username}
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="text-left px-2 py-2.5 text-sm font-medium text-red-500 rounded-xl hover:bg-red-50 transition-colors"
                  >
                    Выйти
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    onClick={() => setMenuOpen(false)}
                    className="px-2 py-2.5 text-sm font-medium text-gray-700 rounded-xl hover:bg-gray-50"
                  >
                    Войти
                  </Link>
                  <Link
                    href="/register"
                    onClick={() => setMenuOpen(false)}
                    className="px-2 py-2.5 text-sm font-semibold text-[#04335A] rounded-xl hover:bg-[#eef3f9] transition-colors"
                  >
                    Регистрация
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
