function S({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-full ${className}`} />
}

function SBox({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-2xl ${className}`} />
}

function CommentSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-5 border border-gray-100 space-y-3">
      <div className="flex items-center gap-3">
        <div className="skeleton w-9 h-9 rounded-full shrink-0" />
        <div className="space-y-1.5 flex-1">
          <S className="h-3 w-28" />
          <S className="h-2.5 w-20" />
        </div>
      </div>
      <S className="h-3 w-full" />
      <S className="h-3 w-10/12" />
      <S className="h-3 w-2/3" />
    </div>
  )
}

export default function ItemLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6">
        <S className="h-3 w-16" />
        <S className="h-3 w-2 !rounded" />
        <S className="h-3 w-20" />
        <S className="h-3 w-2 !rounded" />
        <S className="h-3 w-28" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {/* Gallery skeleton — matches aspect-video gallery */}
        <div className="space-y-3">
          <SBox className="aspect-video w-full !rounded-2xl" />
          <div className="flex gap-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <SBox key={i} className="w-16 h-16 shrink-0 !rounded-xl" />
            ))}
          </div>
        </div>

        {/* Info */}
        <div className="space-y-5">
          <div className="space-y-2">
            <S className="h-3 w-24" />
            <S className="h-8 w-4/5" />
            <S className="h-7 w-3/5" />
          </div>

          {/* Rating */}
          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="skeleton w-5 h-5 rounded" />
              ))}
            </div>
            <S className="h-3 w-24" />
          </div>

          {/* Tags */}
          <div className="flex gap-2 flex-wrap">
            {Array.from({ length: 4 }).map((_, i) => (
              <S key={i} className="h-6 w-16" />
            ))}
          </div>

          {/* Description */}
          <div className="space-y-2 pt-1">
            <S className="h-4 w-full" />
            <S className="h-4 w-11/12" />
            <S className="h-4 w-10/12" />
            <S className="h-4 w-3/4" />
          </div>

          {/* Characteristics table */}
          <div className="mt-2 rounded-xl border border-gray-100 overflow-hidden">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className={`flex items-center px-4 py-3 gap-4 ${i % 2 === 0 ? 'bg-gray-50/80' : 'bg-white'}`}
              >
                <S className={`h-3 w-2/5`} />
                <S className={`h-3 w-1/3`} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recommended products */}
      <div className="mt-16">
        <S className="h-6 w-52 mb-6" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl overflow-hidden border border-gray-100">
              <SBox className="h-40 !rounded-none" />
              <div className="p-3 space-y-2">
                <S className="h-3 w-4/5" />
                <S className="h-3 w-3/5" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comments */}
      <div className="mt-14">
        <S className="h-6 w-40 mb-6" />
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <CommentSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  )
}
