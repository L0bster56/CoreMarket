import { serverGet } from '@/lib/server-fetch'
import type { ApiItemDetail, ApiItemListEntry, ApiItemListResponse } from '@/types'

interface ScoredItem extends ApiItemListEntry {
  score: number
}

/**
 * Returns items scored by relevance to `item`:
 *   +3 for each same-category result
 *   +2 for each shared-tag result
 * Falls back to newest published items if below `limit`.
 */
export async function getRecommendations(
  item: ApiItemDetail,
  limit = 4,
): Promise<ApiItemListEntry[]> {
  type Spec = { p: Promise<ApiItemListResponse>; weight: number }

  // Include the fallback request in the initial parallel batch to avoid
  // a sequential waterfall when category/tag results are insufficient.
  const specs: Spec[] = [
    {
      p: serverGet<ApiItemListResponse>(
        `/items?category_id=${item.category_id}&limit=16&is_published=true`,
        120,
      ),
      weight: 3,
    },
    ...item.tags.slice(0, 2).map((tag) => ({
      p: serverGet<ApiItemListResponse>(
        `/items?tag=${encodeURIComponent(tag.slug)}&limit=8&is_published=true`,
        120,
      ),
      weight: 2,
    })),
    {
      p: serverGet<ApiItemListResponse>(`/items?limit=16&is_published=true`, 120),
      weight: 0,
    },
  ]

  const settled = await Promise.allSettled(specs.map((s) => s.p))
  const scoreMap = new Map<string, ScoredItem>()

  settled.forEach((result, idx) => {
    if (result.status !== 'fulfilled') return
    const { weight } = specs[idx]
    for (const candidate of result.value.items) {
      if (candidate.id === item.id) continue
      const prev = scoreMap.get(candidate.id)
      scoreMap.set(candidate.id, {
        ...(prev ?? candidate),
        score: (prev?.score ?? 0) + weight,
      })
    }
  })

  return [...scoreMap.values()]
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
}
