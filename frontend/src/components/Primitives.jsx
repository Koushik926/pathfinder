import { KIND_STYLE } from '../lib/format'

export function Chip({ children, className = '' }) {
  return <span className={`chip ${className}`}>{children}</span>
}

export function KindChip({ kind }) {
  const style = KIND_STYLE[kind] ?? KIND_STYLE.course
  return <Chip className={style.className}>{style.label}</Chip>
}

export function Meter({ value, className = '', tone = 'accent' }) {
  const tones = { accent: 'bg-accent', mint: 'bg-mint', amber: 'bg-amber' }
  return (
    <div className={`h-1.5 w-full rounded-full bg-ink-line overflow-hidden ${className}`}>
      <div
        className={`h-full rounded-full ${tones[tone]} transition-all duration-700`}
        style={{ width: `${Math.min(100, Math.max(0, (value ?? 0) * 100))}%` }}
      />
    </div>
  )
}

export function Stat({ label, value, hint, tone = 'text-slate-100' }) {
  return (
    <div className="card p-4">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-1 text-2xl font-semibold tabular-nums ${tone}`}>{value}</div>
      {hint && <div className="mt-0.5 text-xs text-slate-500">{hint}</div>}
    </div>
  )
}

export function Spinner({ label = 'Working…' }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-400">
      <span className="inline-block h-3 w-3 rounded-full border-2 border-slate-600 border-t-accent animate-spin" />
      {label}
    </div>
  )
}

export function ErrorNote({ error, onRetry }) {
  if (!error) return null
  return (
    <div className="card border-rose/40 bg-rose/5 p-4 text-sm">
      <div className="font-medium text-rose">Something went wrong</div>
      <div className="mt-1 text-slate-300">{String(error)}</div>
      {onRetry && (
        <button className="btn-ghost mt-3" onClick={onRetry}>Try again</button>
      )}
    </div>
  )
}

export function Empty({ title, children }) {
  return (
    <div className="card p-8 text-center">
      <div className="text-slate-300 font-medium">{title}</div>
      {children && <div className="mt-2 text-sm text-slate-500">{children}</div>}
    </div>
  )
}
