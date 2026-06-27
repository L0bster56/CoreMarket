'use client'

import { usePathname, useSearchParams } from 'next/navigation'
import { useEffect, useRef, useState, Suspense } from 'react'

function ProgressBar() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [phase, setPhase] = useState<'idle' | 'growing' | 'complete'>('idle')
  const prevRouteRef = useRef(pathname + searchParams.toString())
  const isNavigatingRef = useRef(false)
  const completeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const startProgress = () => {
    if (isNavigatingRef.current) return
    isNavigatingRef.current = true
    if (completeTimerRef.current) clearTimeout(completeTimerRef.current)
    setPhase('growing')
  }

  const completeProgress = () => {
    isNavigatingRef.current = false
    setPhase('complete')
    completeTimerRef.current = setTimeout(() => setPhase('idle'), 500)
  }

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const anchor = (e.target as Element).closest('a[href]') as HTMLAnchorElement | null
      if (!anchor) return
      const href = anchor.getAttribute('href') ?? ''
      // Internal navigation only — skip hash links and external
      if (
        (href.startsWith('/') || anchor.hostname === window.location.hostname) &&
        !href.startsWith('#') &&
        !anchor.hasAttribute('download')
      ) {
        startProgress()
      }
    }
    document.addEventListener('click', handleClick, true)
    return () => document.removeEventListener('click', handleClick, true)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const current = pathname + searchParams.toString()
    if (current !== prevRouteRef.current) {
      prevRouteRef.current = current
      if (isNavigatingRef.current) {
        completeProgress()
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname, searchParams])

  useEffect(() => {
    return () => {
      if (completeTimerRef.current) clearTimeout(completeTimerRef.current)
    }
  }, [])

  if (phase === 'idle') return null

  return (
    <div
      aria-hidden="true"
      className="fixed top-0 left-0 right-0 z-[9999] pointer-events-none"
    >
      {/* Thin progress line */}
      <div className="h-[2px] overflow-hidden">
        <div
          className={
            phase === 'complete'
              ? 'h-full bg-gradient-to-r from-[#4474A3] via-[#9ABCED] to-[#4474A3]'
              : 'h-full bg-gradient-to-r from-[#4474A3] via-[#9ABCED] to-[#4474A3] progress-growing'
          }
          style={
            phase === 'complete'
              ? { width: '100%', transition: 'width 0.2s ease-out, opacity 0.3s 0.25s ease-out', opacity: 0 }
              : {}
          }
        />
      </div>
      {/* Subtle glow underneath */}
      <div
        className={
          phase === 'growing'
            ? 'h-[6px] -mt-[6px] bg-gradient-to-r from-transparent via-[#9ABCED]/30 to-transparent progress-growing'
            : 'h-[6px] -mt-[6px]'
        }
        style={phase === 'complete' ? { opacity: 0, transition: 'opacity 0.3s ease-out' } : {}}
      />
    </div>
  )
}

export function NavigationProgress() {
  return (
    <Suspense fallback={null}>
      <ProgressBar />
    </Suspense>
  )
}
