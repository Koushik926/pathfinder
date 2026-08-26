import { useCallback, useEffect, useMemo, useState } from 'react'
import Chat from './components/Chat'
import Dashboard from './components/Dashboard'
import Roadmap from './components/Roadmap'
import { ErrorNote, Spinner } from './components/Primitives'
import { api, clearSession, storeSession, storedSession } from './lib/api'

const GREETING = {
  role: 'assistant',
  text: "Hi — I'm PathFinder. Tell me what you want to be able to do, and I'll build you a learning path that starts from what you already know.",
}

const TABS = [
  { id: 'roadmap', label: 'Roadmap' },
  { id: 'progress', label: 'Progress' },
]

export default function App() {
  const [session, setSession] = useState(null)
  const [meta, setMeta] = useState(null)
  const [turns, setTurns] = useState([GREETING])
  const [options, setOptions] = useState([])
  const [missing, setMissing] = useState(['goal', 'level', 'history', 'pace'])
  const [path, setPath] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [tab, setTab] = useState('roadmap')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  // Boot: reuse a stored session if it still exists, otherwise start a new one.
  useEffect(() => {
    let cancelled = false
    async function boot() {
      try {
        const info = await api.meta()
        if (cancelled) return
        setMeta(info)

        const existing = storedSession()
        if (existing) {
          try {
            const [existingPath, existingDashboard] = await Promise.all([
              api.path(existing),
              api.dashboard(existing),
            ])
            if (cancelled) return
            setSession(existing)
            setPath(existingPath)
            setDashboard(existingDashboard)
            setMissing([])
            setTurns([GREETING, { role: 'assistant', text: 'Welcome back — your path is on the right.' }])
            return
          } catch {
            clearSession()  // session expired server-side; fall through to a new one
          }
        }
        const created = await api.createSession()
        if (cancelled) return
        setSession(created.session_id)
        storeSession(created.session_id)
      } catch (err) {
        if (!cancelled) setError(err.message)
      }
    }
    boot()
    return () => { cancelled = true }
  }, [])

  const refresh = useCallback(async (sessionId) => {
    const [nextPath, nextDashboard] = await Promise.all([
      api.path(sessionId),
      api.dashboard(sessionId),
    ])
    setPath(nextPath)
    setDashboard(nextDashboard)
  }, [])

  const send = useCallback(async (text) => {
    if (!session) return
    setError(null)
    setTurns((current) => [...current, { role: 'learner', text }])
    setOptions([])
    setBusy(true)
    try {
      const result = await api.chat(session, text)
      setTurns((current) => [...current, { role: 'assistant', text: result.reply }])
      setOptions(result.options ?? [])
      setMissing(result.missing_slots ?? [])
      if (result.ready) await refresh(session)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }, [session, refresh])

  const complete = useCallback(async (itemId) => {
    if (!session) return
    setBusy(true)
    try {
      await api.feedback(session, { kind: 'completion', item_id: itemId })
      await refresh(session)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }, [session, refresh])

  const react = useCallback(async (itemId, reaction) => {
    if (!session) return
    setBusy(true)
    try {
      const result = await api.feedback(session, { kind: 'reaction', item_id: itemId, reaction })
      setTurns((current) => [
        ...current,
        { role: 'assistant', text: result.changes.join(' ') },
      ])
      await refresh(session)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }, [session, refresh])

  const explain = useCallback(async (itemId) => {
    if (!session) return
    try {
      setExplanation(await api.explain(session, itemId))
    } catch (err) {
      setError(err.message)
    }
  }, [session])

  async function restart() {
    clearSession()
    setPath(null); setDashboard(null); setExplanation(null)
    setTurns([GREETING]); setOptions([]); setMissing(['goal', 'level', 'history', 'pace'])
    const created = await api.createSession()
    setSession(created.session_id)
    storeSession(created.session_id)
  }

  const completedIds = useMemo(
    () => new Set((dashboard?.profile.completed ?? []).map((c) => c.item_id)),
    [dashboard],
  )

  return (
    <div className="mx-auto flex min-h-screen max-w-[1500px] flex-col px-4 py-5 lg:px-8">
      <header className="mb-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-baseline gap-3">
          <h1 className="text-xl font-bold tracking-tight text-slate-50">
            Path<span className="text-accent">Finder</span>
          </h1>
          <p className="hidden text-sm text-slate-500 sm:block">
            Personalized learning paths, explained
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-500">
          {meta && (
            <span className="hidden md:inline">
              {meta.catalog.items} items · {meta.catalog.skills} skills · {meta.catalog.roles} roles
            </span>
          )}
          {meta && (
            <span className={`chip ${meta.llm.enabled
              ? 'border-mint/40 text-mint bg-mint/10'
              : 'border-ink-line text-slate-500'}`}>
              {meta.llm.enabled ? `Claude · ${meta.llm.model}` : 'Offline mode'}
            </span>
          )}
          <button className="btn-ghost text-xs" onClick={restart}>Start over</button>
        </div>
      </header>

      {error && (
        <div className="mb-4"><ErrorNote error={error} onRetry={() => setError(null)} /></div>
      )}

      <main className="grid flex-1 gap-5 lg:grid-cols-[minmax(340px,420px)_1fr]">
        <div className="h-[calc(100vh-9rem)] lg:sticky lg:top-5">
          <Chat
            session={session}
            turns={turns}
            options={options}
            missing={missing}
            busy={busy}
            onSend={send}
            llmEnabled={meta?.llm.enabled ?? false}
          />
        </div>

        <div className="min-w-0">
          <div className="mb-4 flex gap-1 rounded-lg border border-ink-line bg-ink-soft/50 p-1">
            {TABS.map((entry) => (
              <button
                key={entry.id}
                onClick={() => setTab(entry.id)}
                className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  tab === entry.id ? 'bg-accent-dim text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {entry.label}
              </button>
            ))}
          </div>

          {busy && !path && <div className="mb-3"><Spinner label="Building your path…" /></div>}

          {tab === 'roadmap' ? (
            <Roadmap
              path={path}
              completedIds={completedIds}
              explanation={explanation}
              onExplain={explain}
              onComplete={complete}
              onReact={react}
              busy={busy}
            />
          ) : (
            <Dashboard data={dashboard} onComplete={complete} busy={busy} />
          )}
        </div>
      </main>

      <footer className="mt-8 border-t border-ink-line pt-4 text-xs text-slate-600">
        PathFinder · recommendations are computed locally from a curated catalog;
        every explanation is derived from the ranker's own component attributions.
      </footer>
    </div>
  )
}
