function S({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-full ${className}`} />
}

function SBox({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-2xl ${className}`} />
}

function CardSkeleton() {
  return (
    <div className="bg-white rounded-3xl overflow-hidden border border-gray-100/80 shadow-sm">
      <SBox className="h-60 !rounded-none" />
      <div className="p-5 space-y-3">
        <S className="h-4 w-4/5" />
        <S className="h-3 w-full" />
        <S className="h-3 w-3/4" />
        <div className="pt-3 border-t border-gray-50 flex justify-between items-center">
          <S className="h-3 w-24" />
          <S className="h-3 w-10" />
        </div>
      </div>
    </div>
  )
}

export default function HomeLoading() {
  return (
    <div>
      {/* Hero — matches actual dark hero section */}
      <section className="bg-[#031E36] pt-24 pb-36">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center gap-6">
          <div className="skeleton rounded-full h-7 w-48 opacity-30" />
          <div className="skeleton rounded-2xl h-12 w-3/4 max-w-lg opacity-20" />
          <div className="skeleton rounded-2xl h-10 w-1/2 max-w-sm opacity-20" />
          <div className="skeleton rounded-2xl h-4 w-80 opacity-15" />
          {/* Search bar placeholder */}
          <div className="w-full max-w-2xl mt-2">
            <div className="h-[60px] rounded-2xl bg-white/10" />
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-end justify-between mb-8">
            <div className="space-y-2">
              <S className="h-3 w-20" />
              <S className="h-7 w-36" />
            </div>
            <S className="h-3 w-24" />
          </div>
          <div className="flex gap-3 overflow-hidden">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="shrink-0 w-36 h-24 rounded-2xl overflow-hidden">
                <SBox className="w-full h-full !rounded-2xl" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trending Products */}
      <section className="py-16 bg-[#f0f5fb]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-end justify-between mb-8">
            <div className="space-y-2">
              <S className="h-3 w-24" />
              <S className="h-7 w-44" />
            </div>
            <S className="h-3 w-20" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.from({ length: 6 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        </div>
      </section>

      {/* Blog Preview */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-end justify-between mb-8">
            <div className="space-y-2">
              <S className="h-3 w-16" />
              <S className="h-7 w-40" />
            </div>
            <S className="h-3 w-20" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="bg-white rounded-2xl overflow-hidden border border-gray-100">
                <SBox className="h-44 !rounded-none" />
                <div className="p-5 space-y-3">
                  <S className="h-3 w-20" />
                  <S className="h-5 w-4/5" />
                  <S className="h-3 w-full" />
                  <S className="h-3 w-3/4" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
