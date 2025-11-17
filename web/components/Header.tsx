import Link from 'next/link'

export const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg">
              <span className="text-white font-bold text-lg">c2a</span>
            </div>
            <span className="text-xl font-bold text-gray-900 group-hover:text-blue-600">cli2ansible</span>
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="/sessions" className="text-gray-700 hover:text-blue-600 font-medium transition-colors">
              Sessions
            </Link>
            <Link href="/create" className="text-gray-700 hover:text-blue-600 font-medium transition-colors">
              New Session
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}
