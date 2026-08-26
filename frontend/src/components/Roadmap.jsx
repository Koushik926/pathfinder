import { useState } from 'react'
import { Chip, KindChip, Meter, Empty } from './Primitives'
import { COMPONENT_LABEL, LEVEL_LABEL, humanDate, pct } from '../lib/format'

/** Bar chart of why an item was ranked where it was, from the ranker's own weights. */
function ReasonBars({ components }) {
  const entries = Object.entries(components ?? {}).sort((a, b) => b[1] - a[1])
  if (!entries.length) return null
  const peak = entries[0][1] || 1
  return (
    <div className="mt-3 space-y-1.5">
      {entries.slice(0, 4).map(([name, value]) => (
        <div key={name} className="flex items-center gap-2 text-xs">
          <span className="w-32 shrink-0 text-slate-500">{COMPONENT_LABEL[name] ?? name}</span>
          <div className="h-1.5 flex-1 rounded-full bg-ink-line overflow-hidden">
            <div className="h-full rounded-full bg-accent/70" style={{ width: `${(value / peak) * 100}%` }} />
          </div>
          <span className="w-10 text-right tabular-nums text-slate-500">{value.toFixed(3)}</span>
        </div>
      ))}
    </div>
  )
}

function ItemRow({ item, done, onExplain, onComplete, onReact, busy }) {
  const [open, setOpen] = useState(false)

  return (
    <div className={`rounded-lg border p-3 transition ${
      done ? 'border-mint/30 bg-mint/5' : 'border-ink-line bg-ink/40 hover:border-accent/40'
    }`}>
      <div className="flex items-start gap-3">
        <button
          onClick={() => !done && onComplete(item.item_id)}
          disabled={done || busy}
          title={done ? 'Completed' : 'Mark complete'}
          className={`mt-0.5 h-5 w-5 shrink-0 rounded border text-xs leading-none transition ${
            done
              ? 'border-mint bg-mint text-ink'
              : 'border-slate-600 hover:border-mint hover:text-mint'
          }`}
        >
          {done ? '✓' : ''}
        </button>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`font-medium ${done ? 'text-slate-500 line-through' : 'text-slate-100'}`}>
              {item.title}
            </span>
            <KindChip kind={item.kind} />
            {item.is_prerequisite_fill && (
              <Chip className="border-amber/40 text-amber bg-amber/10">Prerequisite</Chip>
            )}
          </div>

          <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
            <span>{item.provider}</span>
            <span>{item.hours} h</span>
            <span>{LEVEL_LABEL[item.level]}</span>
            <span className="capitalize">{item.modality}</span>
            <span>★ {item.rating}</span>
          </div>

          {item.covers?.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {item.covers.slice(0, 4).map((skill) => (
                <Chip key={skill.id} className="border-ink-line text-slate-400">{skill.name}</Chip>
              ))}
            </div>
          )}

          <div className="mt-2 flex flex-wrap gap-2">
            <button className="text-xs text-accent hover:underline" onClick={() => { setOpen(!open); if (!open) onExplain(item.item_id) }}>
              {open ? 'Hide reasoning' : 'Why this?'}
            </button>
            {!done && (
              <>
                <button className="text-xs text-slate-500 hover:text-amber" onClick={() => onReact(item.item_id, 'too_hard')}>Too hard</button>
                <button className="text-xs text-slate-500 hover:text-amber" onClick={() => onReact(item.item_id, 'too_easy')}>Too easy</button>
                <button className="text-xs text-slate-500 hover:text-rose" onClick={() => onReact(item.item_id, 'not_interested')}>Not for me</button>
                <button className="text-xs text-slate-500 hover:text-mint" onClick={() => onReact(item.item_id, 'loved')}>More like this</button>
              </>
            )}
          </div>

          {open && <ReasonBars components={item.reason_components} />}
        </div>
      </div>
    </div>
  )
}

function Milestone({ milestone, completedIds, ...handlers }) {
  const done = milestone.items.filter((i) => completedIds.has(i.item_id)).length
  const ratio = milestone.items.length ? done / milestone.items.length : 0

  return (
    <section className="relative pl-8">
      <div className="absolute left-0 top-1 flex h-6 w-6 items-center justify-center rounded-full
                      border border-accent/50 bg-ink text-xs font-semibold text-accent">
        {milestone.index}
      </div>
      <div className="absolute left-3 top-8 bottom-0 w-px bg-ink-line" />

      <header className="mb-3">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h3 className="font-semibold text-slate-100">{milestone.title}</h3>
          <span className="text-xs text-slate-500">
            {humanDate(milestone.starts_on)} → {humanDate(milestone.ends_on)}
          </span>
        </div>
        <div className="mt-1 flex items-center gap-3 text-xs text-slate-500">
          <span>{milestone.hours} h · {milestone.weeks} weeks</span>
          <span>{done}/{milestone.items.length} done</span>
        </div>
        <Meter value={ratio} tone="mint" className="mt-2" />
        <div className="mt-2 flex flex-wrap gap-1.5">
          {milestone.focus_skills.map((skill) => (
            <Chip key={skill.id} className="border-accent/30 text-accent/90 bg-accent/5">{skill.name}</Chip>
          ))}
        </div>
      </header>

      <div className="space-y-2 pb-8">
        {milestone.items.map((item) => (
          <ItemRow key={item.item_id} item={item} done={completedIds.has(item.item_id)} {...handlers} />
        ))}
      </div>
    </section>
  )
}

export default function Roadmap({ path, completedIds, explanation, ...handlers }) {
  if (!path) {
    return <Empty title="No path yet">Finish the conversation and your roadmap appears here.</Empty>
  }

  return (
    <div className="space-y-6">
      <div className="card p-5">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">
              {path.role_title ?? 'Your learning path'}
            </h2>
            <p className="mt-0.5 text-sm text-slate-500">
              {path.total_hours} hours · {path.total_weeks} weeks · {path.milestones.length} milestones
            </p>
          </div>
          <div className="text-right">
            <div className="text-xs uppercase tracking-wide text-slate-500">Goal readiness</div>
            <div className="text-xl font-semibold tabular-nums text-slate-100">
              {pct(path.readiness_before)} <span className="text-slate-600">→</span>{' '}
              <span className="text-mint">{pct(path.readiness_after)}</span>
            </div>
          </div>
        </div>

        <ul className="mt-4 space-y-1.5 text-sm text-slate-400">
          {path.narrative.strategy.map((line, index) => (
            <li key={index} className="flex gap-2">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-accent" />
              {line}
            </li>
          ))}
        </ul>
      </div>

      {explanation && (
        <div className="card border-accent/40 p-4 animate-rise">
          <div className="text-sm font-medium text-accent">{explanation.headline}</div>
          {explanation.narrative && (
            <p className="mt-2 text-sm text-slate-300">{explanation.narrative}</p>
          )}
          <ul className="mt-2 space-y-1 text-xs text-slate-400">
            {explanation.reasons.map((reason, index) => <li key={index}>· {reason}</li>)}
          </ul>
          <div className="mt-2 text-[11px] text-slate-600">
            Explanation source: {explanation.source === 'claude' ? 'Claude, from the ranker’s attributions' : 'derived directly from the ranker’s attributions'}
          </div>
        </div>
      )}

      <div>
        {path.milestones.map((milestone) => (
          <Milestone
            key={milestone.index}
            milestone={milestone}
            completedIds={completedIds}
            {...handlers}
          />
        ))}
      </div>
    </div>
  )
}
