import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Страница не найдена',
  robots: { index: false },
}

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[65vh] px-4 text-center">
      <p className="text-8xl font-bold text-[#C4D4E6] leading-none mb-6 select-none">404</p>
      <h1 className="text-2xl font-bold text-[#031E36] mb-3">Страница не найдена</h1>
      <p className="text-gray-500 mb-10 max-w-sm leading-relaxed">
        Запрошенная страница не существует или была удалена. Проверьте адрес или вернитесь в каталог.
      </p>
      <div className="flex gap-3 flex-wrap justify-center">
        <Link
          href="/"
          className="px-6 py-3 bg-[#04335A] text-white font-semibold rounded-xl hover:bg-[#031E36] transition-colors text-sm"
        >
          На главную
        </Link>
        <Link
          href="/catalog"
          className="px-6 py-3 bg-white text-[#04335A] font-semibold rounded-xl border border-[#C4D4E6] hover:bg-[#eef3f9] transition-colors text-sm"
        >
          Каталог
        </Link>
        <Link
          href="/blog"
          className="px-6 py-3 bg-white text-[#04335A] font-semibold rounded-xl border border-[#C4D4E6] hover:bg-[#eef3f9] transition-colors text-sm"
        >
          Блог
        </Link>
      </div>
    </div>
  )
}
