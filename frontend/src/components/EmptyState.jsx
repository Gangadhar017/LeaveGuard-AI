export default function EmptyState({ icon: Icon, title, message, children }) {
  return (
    <div className="card flex flex-col items-center justify-center gap-3 px-6 py-16 text-center animate-fade-in">
      {Icon && (
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-leaf-50">
          <Icon className="h-7 w-7 text-leaf-600" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      {message && <p className="max-w-md text-sm text-slate-500">{message}</p>}
      {children && <div className="mt-2">{children}</div>}
    </div>
  )
}
