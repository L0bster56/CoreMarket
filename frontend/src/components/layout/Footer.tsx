import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-[#031E36] text-gray-400 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 pb-10">

        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pb-10 border-b border-white/10">

          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#04335A] to-[#4474A3] flex items-center justify-center">
                <span className="text-white font-bold text-xs">CM</span>
              </div>
              <span className="font-bold text-white text-lg">CoreMarket</span>
            </div>
            <p className="text-sm leading-relaxed text-gray-500 max-w-[200px]">
              Платформа для сравнения и выбора товаров. Обзоры, характеристики и рейтинги.
            </p>
          </div>

          {/* Catalog */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-xs uppercase tracking-widest">Каталог</h3>
            <ul className="space-y-3 text-sm">
              <li><Link href="/catalog" className="hover:text-white transition-colors">Все товары</Link></li>
              <li><Link href="/catalog/smartphones" className="hover:text-white transition-colors">Смартфоны</Link></li>
              <li><Link href="/catalog/laptops" className="hover:text-white transition-colors">Ноутбуки</Link></li>
            </ul>
          </div>

          {/* Blog */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-xs uppercase tracking-widest">Редакция</h3>
            <ul className="space-y-3 text-sm">
              <li><Link href="/blog" className="hover:text-white transition-colors">Статьи и обзоры</Link></li>
              <li><Link href="/blog" className="hover:text-white transition-colors">Рейтинги</Link></li>
            </ul>
          </div>

          {/* Account */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-xs uppercase tracking-widest">Аккаунт</h3>
            <ul className="space-y-3 text-sm">
              <li><Link href="/login" className="hover:text-white transition-colors">Войти</Link></li>
              <li><Link href="/register" className="hover:text-white transition-colors">Регистрация</Link></li>
              <li><Link href="/profile" className="hover:text-white transition-colors">Профиль</Link></li>
            </ul>
          </div>
        </div>

        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-gray-600">
          <p>© {new Date().getFullYear()} CoreMarket. Все права защищены.</p>
          <p>Находите лучшее быстро.</p>
        </div>
      </div>
    </footer>
  )
}
