import { Chip, Empty, Meter, Stat } from './Primitives'
import { humanDate, pct } from '../lib/format'

/**
 * Skill radar drawn as inline SVG — one polygon for the goal's target profile,
 * one for current mastery. Reading the shaded area against the outline is the
 * fastest way to see where the gaps are.
 */
function SkillRadar({ categories }) {
  const axes = categories.slice(0, 8)
  if (axes.length < 3) return null

  const size = 260
  const center = size / 2
  // Leaves room for the axis labels drawn outside the outer ring.
  const radius = center - 46

  const point = (index, value) => {
    const angle = (Math.PI * 2 * index) / axes.length - Math.PI / 2
    return [
      center + Math.cos(angle) * radius * value,
      center + Math.sin(angle) * radius * value,
    ]
  }
  const polygon = (values) =>
    values.map((value, index) => point(index, value).join(',')).join(' ')

  return (
    <svg viewBox={`-26 0 ${size + 52} ${size}`} className="mx-auto h-64 w-80 max-w-full" role="img"
         aria-label="Skill coverage against the goal profile">
      {[0.25, 0.5, 0.75, 1].map((ring) => (
        <polygon key={ring} points={polygon(axes.map(() => ring))}
                 fill="none" stroke="#232b36" strokeWidth="1" />
      ))}
      {axes.map((_, index) => {
        const [x, y] = point(index, 1)
        return <line key={index} x1={center} y1={center} x2={x} y2={y} stroke="#232b36" strokeWidth="1" />
      })}

      <polygon points={polygon(axes.map(() => 1))} fill="#6ea8fe" fillOpacity="0.06"
               stroke="#6ea8fe" strokeOpacity="0.35" strokeDasharray="3 3" strokeWidth="1" />
      <polygon points={polygon(axes.map((axis) => Math.max(0.04, axis.progress)))}
               fill="#5ddba6" fillOpacity="0.22" stroke="#5ddba6" strokeWidth="1.5" />

      {axes.map((axis, index) => {
        const [x, y] = point(index, 1.18)
        // Anchor by side rather than always centring: a centred label on the
        // leftmost or rightmost axis overflows the viewBox and gets clipped.
        const anchor = x < center - 6 ? 'end' : x > center + 6 ? 'start' : 'middle'
        return (
          <text key={axis.category} x={x} y={y} textAnchor={anchor} dominantBaseline="middle"
                fontSize="8" fill="#7c8798">
            {axis.category.length > 15 ? `${axis.category.slice(0, 14)}…` : axis.category}
          </text>
        )
      })}
    </svg>
  )
}

function GapBar({ gap }) {
  return (
    <div>
      <div className="flex items-baseline justify-between text-xs">
        <span className="text-slate-300">{gap.name}</span>
        <span className="tabular-nums text-slate-500">
          {pct(gap.mastery)} <span className="text-slate-700">/ {pct(gap.target)}</span>
        </span>
      </div>
      <div className="relative mt-1 h-1.5 w-full rounded-full bg-ink-line">
        <div className="absolute inset-y-0 rounded-full bg-accent/25"
             style={{ width: `${gap.target * 100}%` }} />
        <div className="absolute inset-y-0 rounded-full bg-accent"
             style={{ width: `${gap.mastery * 100}%` }} />
      </div>
    </div>
  )
}

export default function Dashboard({ data, onComplete, busy }) {
  if (!data) return <Empty title="No progress yet">Set a goal to start tracking.</Empty>

  const { progress, skills, milestones, next_actions: nextActions } = data

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat label="Goal readiness" value={pct(data.readiness)}
              hint={data.profile.role_title ?? 'custom goal'} tone="text-mint" />
        <Stat label="Path progress" value={pct(progress.percent)}
              hint={`${progress.items_done}/${progress.items_total} items`} />
        <Stat label="Hours invested" value={progress.hours_done}
              hint={`of ${progress.hours_total} planned`} />
        <Stat label="Skills met" value={`${skills.met}/${skills.tracked}`}
              hint={`${skills.open} still open`} tone="text-accent" />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="card p-5">
          <h3 className="font-semibold text-slate-100">Skill coverage</h3>
          <p className="text-xs text-slate-500">
            Solid green is where you are; the dashed outline is what the goal asks for.
          </p>
          <SkillRadar categories={skills.by_category} />
          <div className="mt-2 flex flex-wrap justify-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-sm bg-mint" /> your mastery
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-sm border border-dashed border-accent" /> goal target
            </span>
          </div>
        </section>

        <section className="card p-5">
          <h3 className="font-semibold text-slate-100">Biggest gaps</h3>
          <p className="text-xs text-slate-500">Ranked by how much the goal depends on them.</p>
          <div className="mt-4 space-y-3">
            {skills.top_gaps.length === 0 && (
              <p className="text-sm text-slate-500">Every tracked skill is at target. </p>
            )}
            {skills.top_gaps.map((gap) => <GapBar key={gap.skill_id} gap={gap} />)}
          </div>
        </section>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="card p-5">
          <h3 className="font-semibold text-slate-100">Do next</h3>
          <p className="text-xs text-slate-500">Ready now — every prerequisite is already behind you.</p>
          <div className="mt-4 space-y-2">
            {nextActions.length === 0 && (
              <p className="text-sm text-slate-500">Nothing unlocked right now.</p>
            )}
            {nextActions.map((action) => (
              <div key={action.item_id}
                   className="flex items-center gap-3 rounded-lg border border-ink-line bg-ink/40 p-3">
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-medium text-slate-100">{action.title}</div>
                  <div className="text-xs text-slate-500">
                    {action.provider} · {action.hours} h
                    {action.unlocks > 0 && ` · unlocks ${action.unlocks} more`}
                  </div>
                </div>
                <button className="btn-ghost text-xs" disabled={busy}
                        onClick={() => onComplete(action.item_id)}>
                  Mark done
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className="card p-5">
          <h3 className="font-semibold text-slate-100">Milestones</h3>
          <p className="text-xs text-slate-500">Your plan, phase by phase.</p>
          <div className="mt-4 space-y-3">
            {milestones.map((milestone) => (
              <div key={milestone.index}>
                <div className="flex items-baseline justify-between text-xs">
                  <span className="text-slate-300">{milestone.index}. {milestone.title}</span>
                  <span className="tabular-nums text-slate-500">
                    {milestone.done}/{milestone.total} · {humanDate(milestone.ends_on)}
                  </span>
                </div>
                <Meter value={milestone.total ? milestone.done / milestone.total : 0}
                       tone="mint" className="mt-1" />
              </div>
            ))}
          </div>

          <h4 className="mt-5 text-sm font-medium text-slate-300">Strongest skills</h4>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {skills.strongest.slice(0, 8).map((skill) => (
              <Chip key={skill.skill_id} className="border-mint/30 text-mint bg-mint/5">
                {skill.name} {pct(skill.mastery)}
              </Chip>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
