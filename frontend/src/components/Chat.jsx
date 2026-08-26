import { useEffect, useRef, useState } from 'react'
import { Spinner } from './Primitives'

const SLOT_LABEL = {
  goal: 'Goal',
  level: 'Experience',
  history: 'What you know',
  pace: 'Time',
}

/** The four things PathFinder needs before it can plan. */
function SlotProgress({ missing }) {
  const slots = ['goal', 'level', 'history', 'pace']
  return (
    <div className="flex flex-wrap gap-1.5">
      {slots.map((slot) => {
        const done = !missing.includes(slot)
        return (
          <span
            key={slot}
            className={`chip ${done
              ? 'border-mint/40 text-mint bg-mint/10'
              : 'border-ink-line text-slate-500'}`}
          >
            {done ? '✓' : '○'} {SLOT_LABEL[slot]}
          </span>
        )
      })}
    </div>
  )
}

function Bubble({ turn }) {
  const isLearner = turn.role === 'learner'
  return (
    <div className={`flex ${isLearner ? 'justify-end' : 'justify-start'} animate-rise`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
          isLearner
            ? 'bg-accent-dim/85 text-white rounded-br-sm'
            : 'bg-ink-soft border border-ink-line text-slate-200 rounded-bl-sm'
        }`}
      >
        {turn.text}
      </div>
    </div>
  )
}

export default function Chat({ session, turns, options, missing, busy, onSend, llmEnabled }) {
  const [draft, setDraft] = useState('')
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [turns, busy])

  function submit(event) {
    event?.preventDefault()
    const text = draft.trim()
    if (!text || busy) return
    setDraft('')
    onSend(text)
  }

  return (
    <div className="card flex h-full flex-col overflow-hidden">
      <header className="flex items-center justify-between gap-3 border-b border-ink-line px-4 py-3">
        <div>
          <h2 className="font-semibold text-slate-100">Tell me your goal</h2>
          <p className="text-xs text-slate-500">
            {llmEnabled
              ? 'Claude is reading your replies'
              : 'Running offline — no API key needed'}
          </p>
        </div>
        <SlotProgress missing={missing} />
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {turns.map((turn, index) => <Bubble key={index} turn={turn} />)}
        {busy && (
          <div className="pl-1"><Spinner label="Thinking…" /></div>
        )}
        <div ref={endRef} />
      </div>

      {options.length > 0 && !busy && (
        <div className="flex flex-wrap gap-2 border-t border-ink-line px-4 py-3">
          {options.map((option) => {
            const label = option.label ?? option.title
            return (
              <button
                key={option.value ?? option.item_id}
                className="btn-ghost text-xs"
                onClick={() => onSend(label)}
                title={option.detail ?? option.provider ?? ''}
              >
                {label}
              </button>
            )
          })}
        </div>
      )}

      <form onSubmit={submit} className="flex gap-2 border-t border-ink-line p-3">
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder={session ? 'Type your answer…' : 'Starting…'}
          disabled={!session || busy}
          className="flex-1 rounded-lg bg-ink px-3 py-2 text-sm text-slate-200 border border-ink-line
                     placeholder:text-slate-600 focus:border-accent focus:outline-none disabled:opacity-50"
        />
        <button type="submit" className="btn-primary" disabled={!draft.trim() || busy}>
          Send
        </button>
      </form>
    </div>
  )
}
