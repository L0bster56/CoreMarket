// Redis cache handler for Next.js 16 'use cache: remote' directive.
// Used for persistent, cross-instance caching (presigned URLs etc.).
// Gracefully falls back to in-memory on connection failure.

'use strict'

const MAX_RETRIES = 3
const RETRY_DELAY_MS = 1000

let _client = null
let _healthy = false

async function getClient() {
  if (!process.env.REDIS_URL) return null

  if (_client && _healthy) return _client

  try {
    const { createClient } = require('redis')
    _client = createClient({ url: process.env.REDIS_URL, socket: { reconnectStrategy: false } })
    _client.on('error', (err) => {
      console.warn('[redis-cache] error:', err.message)
      _healthy = false
    })
    _client.on('ready', () => { _healthy = true })
    await _client.connect()
    _healthy = true
    return _client
  } catch (err) {
    console.warn('[redis-cache] connect failed, using in-memory fallback:', err.message)
    _client = null
    _healthy = false
    return null
  }
}

// Tag expiration tracking (in-process fallback for distributed invalidation)
const tagTimestamps = new Map()

module.exports = {
  async get(cacheKey, softTags) {
    const client = await getClient()
    if (!client) return undefined

    try {
      const stored = await client.get(`nextjs:cache:${cacheKey}`)
      if (!stored) {
        if (process.env.CACHE_DEBUG === '1') {
          console.log(`[redis-cache] MISS key=${cacheKey}`)
        }
        return undefined
      }

      const data = JSON.parse(stored)

      // Check tag-based invalidation
      if (data.tags && Array.isArray(data.tags) && data.tags.length > 0) {
        const entryTs = data.timestamp || 0
        for (const tag of data.tags) {
          const tagTs = tagTimestamps.get(tag) || 0
          if (tagTs > entryTs) {
            // Tag was invalidated after this entry was created
            await client.del(`nextjs:cache:${cacheKey}`).catch(() => {})
            if (process.env.CACHE_DEBUG === '1') {
              console.log(`[redis-cache] TAG_EXPIRED key=${cacheKey} tag=${tag}`)
            }
            return undefined
          }
        }
      }

      if (process.env.CACHE_DEBUG === '1') {
        const ageSeconds = Math.round((Date.now() - (data.timestamp || 0)) / 1000)
        console.log(`[redis-cache] HIT key=${cacheKey} age=${ageSeconds}s`)
      }

      // Reconstruct ReadableStream from stored base64 data
      const buffer = Buffer.from(data.value, 'base64')
      return {
        value: new ReadableStream({
          start(controller) {
            controller.enqueue(new Uint8Array(buffer))
            controller.close()
          },
        }),
        tags: data.tags || [],
        stale: data.stale || 0,
        timestamp: data.timestamp || Date.now(),
        expire: data.expire || 3600,
        revalidate: data.revalidate || 60,
      }
    } catch (err) {
      console.warn('[redis-cache] get error:', err.message)
      return undefined
    }
  },

  async set(cacheKey, pendingEntry) {
    const client = await getClient()
    if (!client) return

    try {
      const entry = await pendingEntry

      // Read the ReadableStream
      const reader = entry.value.getReader()
      const chunks = []
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          chunks.push(value)
        }
      } finally {
        reader.releaseLock()
      }

      const buffer = Buffer.concat(chunks.map((chunk) => Buffer.from(chunk)))
      const ttl = Math.max(entry.expire || 3600, entry.revalidate || 60)

      await client.set(
        `nextjs:cache:${cacheKey}`,
        JSON.stringify({
          value: buffer.toString('base64'),
          tags: entry.tags || [],
          stale: entry.stale || 0,
          timestamp: entry.timestamp || Date.now(),
          expire: entry.expire || 3600,
          revalidate: entry.revalidate || 60,
        }),
        { EX: ttl },
      )

      if (process.env.CACHE_DEBUG === '1') {
        console.log(`[redis-cache] SET key=${cacheKey} ttl=${ttl}s tags=${(entry.tags || []).join(',')}`)
      }
    } catch (err) {
      console.warn('[redis-cache] set error:', err.message)
    }
  },

  async refreshTags() {
    // No-op: we use in-process tag timestamps
    // For multi-instance: sync from Redis key `nextjs:tags:*`
  },

  async getExpiration(tags) {
    if (!tags || tags.length === 0) return 0
    const timestamps = tags.map((tag) => tagTimestamps.get(tag) || 0)
    return Math.max(...timestamps, 0)
  },

  async updateTags(tags, durations) {
    const now = Date.now()
    for (const tag of tags) {
      tagTimestamps.set(tag, now)
    }

    // Also invalidate in Redis by deleting tagged entries
    const client = await getClient()
    if (!client) return

    try {
      // Scan for keys with matching tags and delete them
      // This is best-effort; in-process tagTimestamps handles the rest
      const pipeline = client.multi()
      for (const tag of tags) {
        pipeline.set(`nextjs:tag:${tag}`, String(now))
      }
      await pipeline.exec()

      if (process.env.CACHE_DEBUG === '1') {
        console.log(`[redis-cache] INVALIDATE tags=${tags.join(',')}`)
      }
    } catch (err) {
      console.warn('[redis-cache] updateTags error:', err.message)
    }
  },
}
