import { Link } from 'react-router-dom'
import { WifiOff } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="mx-auto flex max-w-xl flex-col items-center px-4 py-24 text-center">
      <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-leaf-50">
        <WifiOff className="h-8 w-8 text-leaf-600" />
      </span>
      <h1 className="mt-6 text-4xl font-extrabold text-slate-900">404</h1>
      <p className="mt-2 text-slate-500">The page you are looking for doesn't exist.</p>
      <Link to="/" className="btn-primary mt-8">
        Back to Home
      </Link>
    </div>
  )
}
