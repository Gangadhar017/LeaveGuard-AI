export function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatConfidence(value) {
  if (value === null || value === undefined) return '—'
  return `${Number(value).toFixed(2)}%`
}

export function truncate(text, length = 60) {
  if (!text) return ''
  return text.length > length ? `${text.slice(0, length - 1)}…` : text
}

export const SEVERITY_STYLES = {
  healthy: 'bg-leaf-100 text-leaf-800 ring-leaf-200',
  low: 'bg-sky-100 text-sky-800 ring-sky-200',
  medium: 'bg-amber-100 text-amber-800 ring-amber-200',
  high: 'bg-orange-100 text-orange-800 ring-orange-200',
  critical: 'bg-red-100 text-red-800 ring-red-200',
  unknown: 'bg-slate-100 text-slate-700 ring-slate-200',
}
