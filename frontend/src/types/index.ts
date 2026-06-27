export interface Category {
  id: string
  name: string
  slug: string
  description: string | null
  image_url: string | null  // storage key e.g. "categories/uuid.jpg" — resolve via presigned-cache
  created_at: string
}

export interface Tag {
  id: string
  name: string
  slug: string
}

export interface Characteristic {
  id: string
  item_id?: string
  group?: string | null
  name: string
  value: string
}

export interface GalleryImage {
  id: string
  item_id?: string
  image_url: string  // storage key e.g. "items/uuid.jpg" — resolve via presigned-cache
}

export interface MarketplaceLink {
  name: string
  url: string
  price?: string | null
}

export interface Item {
  id: string
  category_id: string
  title: string
  short_description: string
  full_description?: string
  preview_image?: string  // storage key e.g. "items/uuid.jpg" — resolve via presigned-cache
  is_published: boolean
  created_at: string
  updated_at: string
  youtube_url?: string | null
  marketplace_links?: MarketplaceLink[]
  category?: Category
  tags?: Tag[]
  characteristics?: Characteristic[]
  gallery?: GalleryImage[]
  avg_rating?: number
  rating_count?: number
  view_count?: number
}

export interface User {
  id: string
  username: string
  email: string
  role: 'admin' | 'user'
  avatar_url?: string | null  // storage key e.g. "users/uuid.jpg" — resolve via presigned-cache
  created_at: string
}

export interface Comment {
  id: string
  item_id: string
  user_id: string
  parent_id?: string
  text: string
  is_deleted: boolean
  created_at: string
  updated_at: string
  user?: User
  replies?: Comment[]
}

export interface Rating {
  id: string
  item_id: string
  user_id: string
  score: number
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface ItemFilters {
  search?: string
  category_id?: string
  tag?: string
  min_rating?: number
  limit?: number
  offset?: number
}

// Backend API response types

export interface ApiItemListEntry {
  id: string
  title: string
  short_description: string
  category_id: string
  youtube_url: string | null
  is_published: boolean
  view_count: number
  created_at: string
  updated_at: string
  preview_image: string | null
}

export interface ApiItemListResponse {
  items: ApiItemListEntry[]
  total: number
}

export interface ApiItemDetail {
  id: string
  title: string
  short_description: string
  description: string
  category_id: string
  youtube_url: string | null
  marketplace_links: MarketplaceLink[]
  is_published: boolean
  view_count: number
  characteristics: Characteristic[]
  gallery: GalleryImage[]
  tags: Tag[]
  created_at: string
  updated_at: string
}

export interface RatingInfo {
  average: number | null
  count: number
  user_score: number | null
}

export interface ApiComment {
  id: string
  user_id: string
  parent_id: string | null
  body: string
  is_deleted: boolean
  created_at: string
  children: ApiComment[]
}

// ── Blog ──────────────────────────────────────────────────────────────────────

export interface BlogTag {
  id: string
  name: string
  slug: string
}

export interface BlogProductLink {
  id: string
  product_id: string
  display_order: number
}

export type BlogPostStatus = 'draft' | 'published' | 'archived'

export interface BlogPostListEntry {
  id: string
  title: string
  slug: string
  short_description: string | null
  cover_image_url: string | null  // storage key e.g. "blog/uuid.jpg" — resolve via presigned-cache
  category_id: string | null
  status: BlogPostStatus
  created_at: string
  updated_at: string
}

export interface BlogPost {
  id: string
  title: string
  slug: string
  short_description: string | null
  content: string | null
  content_html: string | null
  cover_image_url: string | null  // storage key e.g. "blog/uuid.jpg" — resolve via presigned-cache
  category_id: string | null
  category: { id: string; name: string; slug: string } | null
  status: BlogPostStatus
  seo_title: string | null
  seo_description: string | null
  tags: BlogTag[]
  product_links: BlogProductLink[]
  created_at: string
  updated_at: string
}

export interface BlogListResponse {
  items: BlogPostListEntry[]
  total: number
}
