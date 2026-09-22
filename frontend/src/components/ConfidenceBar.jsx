export default function ConfidenceBar({ value, className = '' }) {
  const clamped = Math.max(0, Math.min(100, Number(value) || 0))
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div
        className="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-200"
        role="progressbar"
        aria-valuenow={Math.round(clamped)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Model confidence"
      >
        <div
          className="h-full rounded-full bg-gradient-to-r from-leaf-500 to-leaf-600 transition-[width] duration-700 ease-out"
          style={{ width: `${clamped}%` }}
        />
      </div>
      <span className="w-16 text-right text-sm font-bold tabular-nums text-slate-800">
        {clamped.toFixed(2)}%
      </span>
    </div>
  )
}
