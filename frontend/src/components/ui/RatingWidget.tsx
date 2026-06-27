'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { getRating, createRating, updateRating, deleteRating } from '@/services/ratings'

const StarPath =
  'M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z'

interface Props {
  itemId: string
  initialAverage: number | null
  initialCount: number
}

export default function RatingWidget({ itemId, initialAverage, initialCount }: Props) {
  const { user } = useAuth()
  const [average, setAverage] = useState<number | null>(initialAverage)
  const [count, setCount] = useState(initialCount)
  const [userScore, setUserScore] = useState<number | null>(null)
  const [hovered, setHovered] = useState(0)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!user) return
    let cancelled = false
    getRating(itemId)
      .then((r) => { if (!cancelled) setUserScore(r.user_score) })
      .catch(() => {})
    return () => { cancelled = true }
  }, [user, itemId])

  const syncFromServer = async () => {
    const r = await getRating(itemId)
    setAverage(r.average)
    setCount(r.count)
    setUserScore(r.user_score)
  }

  const handleRate = async (score: number) => {
    if (loading) return
    setLoading(true)
    const prevScore = userScore
    const prevAverage = average
    const prevCount = count

    // Optimistic update: score + average + count
    setUserScore(score)
    if (prevScore === null) {
      const newCount = count + 1
      setCount(newCount)
      setAverage(average !== null ? (average * count + score) / newCount : score)
    } else {
      setAverage(average !== null && count > 0 ? (average * count - prevScore + score) / count : score)
    }

    try {
      if (prevScore === null) {
        await createRating(itemId, score)
      } else {
        await updateRating(itemId, score)
      }
      await syncFromServer()
    } catch {
      setUserScore(prevScore)
      setAverage(prevAverage)
      setCount(prevCount)
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async () => {
    if (loading || userScore === null) return
    setLoading(true)
    const prevScore = userScore
    const prevAverage = average
    const prevCount = count

    // Optimistic update
    setUserScore(null)
    const newCount = count - 1
    setCount(newCount)
    setAverage(newCount > 0 && average !== null ? (average * count - prevScore) / newCount : null)

    try {
      await deleteRating(itemId)
      await syncFromServer()
    } catch {
      setUserScore(prevScore)
      setAverage(prevAverage)
      setCount(prevCount)
    } finally {
      setLoading(false)
    }
  }

  const displayScore = hovered || userScore || 0

  return (
    <div className="mt-3 flex flex-wrap items-center gap-4">
      {/* Average stars (static display) */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-0.5">
          {[1, 2, 3, 4, 5].map((star) => (
            <svg
              key={star}
              className={`w-5 h-5 ${
                average !== null && star <= Math.round(average)
                  ? 'text-amber-400'
                  : 'text-gray-300'
              }`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d={StarPath} />
            </svg>
          ))}
        </div>
        {average !== null ? (
          <span className="text-sm font-semibold text-gray-700">
            {average.toFixed(1)}{' '}
            <span className="text-gray-400 font-normal text-xs">({count})</span>
          </span>
        ) : (
          <span className="text-sm text-gray-400">Оценок пока нет</span>
        )}
      </div>

      {/* Interactive stars for logged-in users */}
      {user && (
        <div className="flex items-center gap-2 border-l border-gray-200 pl-4">
          <span className="text-xs text-gray-400 whitespace-nowrap">Ваша оценка:</span>
          <div className="flex items-center gap-0.5">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                onMouseEnter={() => setHovered(star)}
                onMouseLeave={() => setHovered(0)}
                onClick={() => handleRate(star)}
                disabled={loading}
                className="focus:outline-none disabled:cursor-not-allowed"
                aria-label={`Оценить ${star} из 5`}
              >
                <svg
                  className={`w-6 h-6 transition-colors ${
                    star <= displayScore
                      ? 'text-amber-400'
                      : 'text-gray-300 hover:text-amber-300'
                  }`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d={StarPath} />
                </svg>
              </button>
            ))}
          </div>
          {userScore !== null && (
            <button
              onClick={handleRemove}
              disabled={loading}
              className="text-xs text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50"
            >
              Убрать
            </button>
          )}
        </div>
      )}
    </div>
  )
}
