export default function StatCard({ icon: Icon, label, value, tone = 'text-leaf-600', sub }) {
  return (
    <div className="card flex items-center gap-4 p-5">
      <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-100`}>
        <Icon className={`h-5 w-5 ${tone}`} />
      </span>
      <div className="min-w-0">
        <p className="truncate text-xs font-semibold uppercase tracking-wider text-slate-400">{label}</p>
        <p className="truncate text-xl font-bold text-slate-900">{value}</p>
        {sub && <p className="truncate text-xs text-slate-400">{sub}</p>}
      </div>
    </div>
  )
}
