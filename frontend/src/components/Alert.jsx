import { AlertTriangle, X } from 'lucide-react'

export default function Alert({ title = 'Something went wrong', message, onDismiss }) {
  if (!message) return null
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 animate-fade-in"
    >
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-500" />
      <div className="flex-1">
        <p className="text-sm font-semibold text-red-800">{title}</p>
        <p className="mt-0.5 text-sm text-red-700">{message}</p>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} aria-label="Dismiss error" className="rounded p-1 text-red-400 hover:bg-red-100 hover:text-red-600">
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}
