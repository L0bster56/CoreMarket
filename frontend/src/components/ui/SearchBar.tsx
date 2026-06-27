interface SearchBarProps {
  placeholder?: string
  className?: string
  initialValue?: string
}

export default function SearchBar({ placeholder = 'Поиск...', className = '', initialValue = '' }: SearchBarProps) {
  return (
    <form action="/catalog" method="GET" className={`w-full ${className}`}>
      <div className="flex gap-2 p-1.5 bg-white rounded-2xl shadow-sm border border-gray-200/80 focus-within:border-[#9ABCED] focus-within:shadow-md transition-all">
        <div className="relative flex-1">
          <svg
            className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            name="search"
            defaultValue={initialValue}
            placeholder={placeholder}
            className="w-full pl-10 pr-4 py-2.5 text-sm text-[#031E36] bg-transparent focus:outline-none placeholder:text-gray-400"
          />
        </div>
        <button
          type="submit"
          className="px-5 py-2.5 bg-[#04335A] hover:bg-[#031E36] text-white text-sm font-semibold rounded-xl transition-colors shrink-0"
        >
          Найти
        </button>
      </div>
    </form>
  )
}
