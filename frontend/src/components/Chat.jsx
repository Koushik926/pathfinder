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
  const answered = slots.filter((slot) => !missing.includes(slot)).length
  return (
    <ul
      className="flex flex-wrap gap-1.5"
      aria-label={`Profile questions answered: ${answered} of ${slots.length}`}
    >
      {slots.map((slot) => {
        const done = !missing.includes(slot)
        return (
          <li
            key={slot}
            className={`chip ${done
              ? 'border-mint/40 text-mint bg-mint/10'
              : 'border-ink-line text-slate-500'}`}
          >
            {/* The glyph carries the state visually; the text carries it
                for anyone who cannot see the glyph. */}
            <span aria-hidden="true">{done ? '✓' : '○'}</span>
            {SLOT_LABEL[slot]}
            <span className="sr-only">{done ? ' — answered' : ' — still needed'}</span>
          </li>
        )
      })}
    </ul>
  )
}

function Bubble({ turn }) {
  const isLearner = turn.role === 'learner'
  return (
    <div className={`flex ${isLearner ? 'justify-end' : 'justify-start'} animate-rise`}>
      {/* Which side of the transcript a bubble sits on is the only thing
          identifying the speaker, and that is invisible to a screen reader. */}
      <span className="sr-only">{isLearner ? 'You said: ' : 'PathFinder said: '}</span>
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

// Once a path exists the assistant answers questions about it, but nobody
// discovers that from a blank input box. These are the questions learners
// actually ask, offered as one tap.
const STARTER_QUESTIONS = [
  'What should I do first?',
  'How long will this take?',
  'Why is it in this order?',
  'Can I go faster?',
]

export default function Chat({ session, turns, options, missing, busy, onSend, llmEnabled, hasPath }) {
  const [draft, setDraft] = useState('')
  const scrollRef = useRef(null)

  // Scroll the transcript container directly. scrollIntoView() walks up to the
  // nearest scrollable ancestor — which is the document — so on load with a
  // restored session it dragged the whole page down and hid the header and the
  // path summary entirely.
  useEffect(() => {
    const box = scrollRef.current
    if (!box) return
    const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    box.scrollTo({ top: box.scrollHeight, behavior: reduced ? 'auto' : 'smooth' })
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
      <header className="space-y-2.5 border-b border-ink-line px-4 py-3">
        <div className="flex items-baseline justify-between gap-3">
          <h2 className="font-semibold text-slate-100">Tell me your goal</h2>
          <p className="shrink-0 text-xs text-slate-500">
            {llmEnabled ? 'Claude enabled' : 'Offline — no API key'}
          </p>
        </div>
        <SlotProgress missing={missing} />
      </header>

      {/* role="log" with a polite live region means new replies are announced
          as they arrive, without interrupting whatever is being read.
          tabIndex makes the scrollable transcript reachable by keyboard. */}
      <div
        ref={scrollRef}
        role="log"
        aria-live="polite"
        aria-label="Conversation"
        aria-busy={busy}
        tabIndex={0}
        className="flex-1 space-y-3 overflow-y-auto px-4 py-4"
      >
        {turns.map((turn, index) => <Bubble key={index} turn={turn} />)}
        {busy && (
          <div className="pl-1"><Spinner label="Thinking…" /></div>
        )}
      </div>

      {hasPath && options.length === 0 && !busy && (
        <div className="border-t border-ink-line px-4 py-3">
          <div id="starter-label" className="mb-2 text-xs text-slate-500">Ask me about your path</div>
          <div className="flex flex-wrap gap-2" role="group" aria-labelledby="starter-label">
            {STARTER_QUESTIONS.map((question) => (
              <button key={question} className="btn-ghost text-xs" onClick={() => onSend(question)}>
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {options.length > 0 && !busy && (
        <div
          className="flex flex-wrap gap-2 border-t border-ink-line px-4 py-3"
          role="group"
          aria-label="Suggested answers"
        >
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
        <label htmlFor="chat-input" className="sr-only">Your message to PathFinder</label>
        <input
          id="chat-input"
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
