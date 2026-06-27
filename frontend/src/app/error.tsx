'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('[CoreMarket error]', error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 text-center">
      <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center mb-5">
        <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <h2 className="text-2xl font-bold text-[#031E36] mb-2">Что-то пошло не так</h2>
      <p className="text-gray-500 mb-8 max-w-sm">
        Произошла ошибка при загрузке страницы. Попробуйте обновить или вернитесь позже.
      </p>
      <div className="flex gap-3">
        <button
          onClick={reset}
          className="px-6 py-3 bg-[#04335A] text-white font-semibold rounded-xl hover:bg-[#031E36] transition-colors text-sm"
        >
          Попробовать снова
        </button>
        <a
          href="/"
          className="px-6 py-3 bg-white text-[#04335A] font-semibold rounded-xl border border-[#C4D4E6] hover:bg-[#eef3f9] transition-colors text-sm"
        >
          На главную
        </a>
      </div>
      {error.digest && (
        <p className="mt-6 text-xs text-gray-400 font-mono">ID: {error.digest}</p>
      )}
    </div>
  )
}
