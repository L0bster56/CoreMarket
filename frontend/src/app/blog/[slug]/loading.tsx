function S({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-full ${className}`} />
}

function SBox({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-2xl ${className}`} />
}

export default function BlogPostLoading() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-8">
        <S className="h-3 w-14" />
        <S className="h-3 w-2 !rounded" />
        <S className="h-3 w-20" />
        <S className="h-3 w-2 !rounded" />
        <S className="h-3 w-32" />
      </div>

      {/* Post header */}
      <div className="mb-8 space-y-4">
        {/* Category badge */}
        <S className="h-6 w-28" />
        {/* Title */}
        <S className="h-10 w-11/12" />
        <S className="h-9 w-4/5" />
        {/* Excerpt */}
        <S className="h-4 w-full max-w-2xl" />
        <S className="h-4 w-3/4 max-w-xl" />
        {/* Meta */}
        <div className="flex items-center gap-4 pt-2">
          <div className="flex items-center gap-2">
            <div className="skeleton w-8 h-8 rounded-full shrink-0" />
            <S className="h-3 w-24" />
          </div>
          <S className="h-3 w-28" />
          <div className="flex gap-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <S key={i} className="h-5 w-16" />
            ))}
          </div>
        </div>
      </div>

      {/* Cover image */}
      <SBox className="mb-10 w-full aspect-[21/9] !rounded-2xl" />

      {/* Article body lines */}
      <div className="space-y-3 mb-6">
        {[...Array(5)].map((_, i) => (
          <S key={i} className="h-4 w-full" />
        ))}
        <S className="h-4 w-2/3" />
      </div>
      {/* Paragraph break */}
      <div className="space-y-3 mb-6">
        {[...Array(4)].map((_, i) => (
          <S key={i} className={`h-4 ${i === 3 ? 'w-1/2' : 'w-full'}`} />
        ))}
      </div>
      {/* Blockquote-like */}
      <div className="border-l-4 border-gray-200 pl-4 mb-6 space-y-2">
        <S className="h-4 w-11/12" />
        <S className="h-4 w-10/12" />
      </div>
      <div className="space-y-3 mb-12">
        {[...Array(4)].map((_, i) => (
          <S key={i} className={`h-4 ${i === 3 ? 'w-3/5' : 'w-full'}`} />
        ))}
      </div>

      {/* Related products */}
      <div className="border-t border-gray-100 pt-10">
        <S className="h-4 w-40 mb-5" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="space-y-2">
              <SBox className="aspect-square !rounded-xl" />
              <S className="h-3 w-full" />
              <S className="h-3 w-3/4" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
