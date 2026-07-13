import { useState } from 'react'
import { useScore, calcLiveScore } from '../context/ScoreContext'
import { Trophy, Clock, MessageSquare, Flag, CheckCircle2, Send, AlertCircle } from 'lucide-react'

interface ScoringPanelProps {
  challengeId: string
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

export default function ScoringPanel({ challengeId }: ScoringPanelProps) {
  const { scores, submitChallengeFlag } = useScore()
  const [flagInput, setFlagInput] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; msg: string } | null>(null)

  const state = scores[challengeId] ?? { elapsedSeconds: 0, queryCount: 0, solved: false, lockedScore: null }
  const liveScore = state.solved && state.lockedScore !== null
    ? state.lockedScore
    : calcLiveScore(state.elapsedSeconds, state.queryCount)

  const handleSubmit = async () => {
    if (!flagInput.trim() || submitting) return
    setSubmitting(true)
    setFeedback(null)

    const res = await submitChallengeFlag(challengeId, flagInput.trim())

    if (res.success) {
      setFeedback({ type: 'success', msg: `Flag accepted! Score: ${res.score}` })
      setFlagInput('')
    } else {
      setFeedback({ type: 'error', msg: res.error || 'Incorrect flag.' })
    }
    setSubmitting(false)
  }

  return (
    <div className="border-b border-white/[0.05] p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Trophy size={13} className={state.solved ? 'text-green' : 'text-orange'} />
        <h3 className="font-mono text-sm font-bold text-primary uppercase tracking-wider">
          Challenge Score
        </h3>
      </div>

      {/* Live metrics row */}
      <div className="grid grid-cols-3 gap-2">
        {/* Time */}
        <div className="glass rounded p-2.5 text-center space-y-1">
          <Clock size={12} className="text-cyan mx-auto" />
          <p className="font-mono text-xs text-muted uppercase tracking-wider leading-none">Time</p>
          <p className={`font-mono text-sm font-bold ${state.solved ? 'text-sub' : 'text-primary'}`}>
            {formatTime(state.elapsedSeconds)}
          </p>
        </div>

        {/* Queries */}
        <div className="glass rounded p-2.5 text-center space-y-1">
          <MessageSquare size={12} className="text-cyan mx-auto" />
          <p className="font-mono text-xs text-muted uppercase tracking-wider leading-none">Queries</p>
          <p className={`font-mono text-sm font-bold ${state.solved ? 'text-sub' : 'text-primary'}`}>
            {state.queryCount}
          </p>
        </div>

        {/* Score */}
        <div className={`glass rounded p-2.5 text-center space-y-1 ${state.solved ? 'border-green/20' : ''}`}>
          <Trophy size={12} className={`mx-auto ${state.solved ? 'text-green' : 'text-orange'}`} />
          <p className="font-mono text-xs text-muted uppercase tracking-wider leading-none">Score</p>
          <p className={`font-mono text-sm font-bold ${
            state.solved
              ? 'text-green'
              : liveScore > 500
                ? 'text-primary'
                : liveScore > 200
                  ? 'text-orange'
                  : 'text-red'
          }`}>
            {liveScore}
          </p>
        </div>
      </div>

      {/* Score progress bar */}
      <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${
            state.solved
              ? 'bg-green'
              : liveScore > 500
                ? 'bg-cyan'
                : liveScore > 200
                  ? 'bg-orange'
                  : 'bg-red'
          }`}
          style={{ width: `${Math.min(100, (liveScore / 1000) * 100)}%` }}
        />
      </div>

      {/* Penalty info */}
      <div className="flex items-center justify-between text-[9px] font-mono text-muted">
        <span>−0.5 pts/sec</span>
        <span>−20 pts/query</span>
      </div>

      {/* Flag submission */}
      {state.solved ? (
        <div className="flex items-center gap-2 p-3 border border-green/30 bg-green/5 rounded text-xs font-mono text-green">
          <CheckCircle2 size={14} className="shrink-0" />
          <span className="font-bold">CHALLENGE COMPLETE — Score locked at {state.lockedScore}</span>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Flag size={12} className="text-cyan shrink-0" />
            <span className="font-mono text-xs text-sub">Submit Flag</span>
          </div>
          <div className="flex gap-2">
            <input
              id={`flag-input-${challengeId}`}
              type="text"
              value={flagInput}
              onChange={e => setFlagInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSubmit()}
              placeholder="FLAG{...}"
              className="flex-1 bg-white/[0.04] border border-white/[0.08] rounded px-3 py-2 text-xs font-mono text-primary placeholder:text-muted/50 outline-none focus:border-cyan/40 transition-colors"
            />
            <button
              id={`flag-submit-${challengeId}`}
              onClick={handleSubmit}
              disabled={submitting || !flagInput.trim()}
              className="px-3 py-2 bg-cyan/10 border border-cyan/20 rounded text-xs font-mono font-bold text-cyan hover:bg-cyan/20 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
            >
              <Send size={11} />
              {submitting ? '...' : 'Submit'}
            </button>
          </div>
        </div>
      )}

      {/* Feedback message */}
      {feedback && (
        <div className={`flex items-center gap-2 p-2.5 rounded text-xs font-mono animate-fade-in ${
          feedback.type === 'success'
            ? 'border border-green/30 bg-green/5 text-green'
            : 'border border-red/30 bg-red/5 text-red'
        }`}>
          {feedback.type === 'success'
            ? <CheckCircle2 size={13} className="shrink-0" />
            : <AlertCircle size={13} className="shrink-0" />
          }
          <span>{feedback.msg}</span>
        </div>
      )}
    </div>
  )
}
