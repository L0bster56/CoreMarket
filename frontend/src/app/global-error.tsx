'use client'

import { useEffect } from 'react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('[CoreMarket global error]', error)
  }, [error])

  return (
    <html lang="ru">
      <body
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#f0f5fb',
          fontFamily: 'system-ui, sans-serif',
          padding: '1rem',
          textAlign: 'center',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#031E36', marginBottom: '0.5rem' }}>
            CoreMarket
          </h1>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem', maxWidth: '360px' }}>
            Произошла критическая ошибка. Попробуйте обновить страницу.
          </p>
          <button
            onClick={reset}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#04335A',
              color: '#fff',
              fontWeight: 600,
              borderRadius: '0.75rem',
              border: 'none',
              cursor: 'pointer',
              fontSize: '0.875rem',
            }}
          >
            Обновить страницу
          </button>
        </div>
      </body>
    </html>
  )
}
