import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react'
import type { ChallengeScoreState } from '../types'
import { submitFlag } from '../api/client'

/* ── Helpers ───────────────────────────────────────────────────────────────── */

const STORAGE_KEY = 'aavai-score-state'
const SESSION_KEY = 'aavai-session-id'

function getSessionId(): string {
  let id = sessionStorage.getItem(SESSION_KEY)
  if (!id) {
    id = crypto.randomUUID()
    sessionStorage.setItem(SESSION_KEY, id)
  }
  return id
}

function defaultState(): ChallengeScoreState {
  return { elapsedSeconds: 0, queryCount: 0, solved: false, lockedScore: null }
}

type ScoreMap = Record<string, ChallengeScoreState>

function loadState(): ScoreMap {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function saveState(map: ScoreMap) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(map))
}

/* ── Scoring constants (mirrored from backend) ─────────────────────────────── */
const STARTING_SCORE = 1000
const TIME_PENALTY   = 0.5
const QUERY_PENALTY  = 20

export function calcLiveScore(elapsed: number, queries: number): number {
  return Math.max(0, Math.floor(STARTING_SCORE - elapsed * TIME_PENALTY - queries * QUERY_PENALTY))
}

/* ── Context shape ─────────────────────────────────────────────────────────── */

interface ScoreCtx {
  /** Full map of challenge states */
  scores: ScoreMap
  /** Set which challenge is currently active (timer ticks for this one) */
  setActiveChallenge: (id: string | null) => void
  /** Increment query counter for a challenge */
  incrementQueries: (id: string) => void
  /** Submit a flag — returns { success, score?, error? } */
  submitChallengeFlag: (
    challengeId: string,
    flag: string
  ) => Promise<{ success: boolean; score?: number; error?: string }>
}

const Ctx = createContext<ScoreCtx>({
  scores: {},
  setActiveChallenge: () => {},
  incrementQueries: () => {},
  submitChallengeFlag: async () => ({ success: false }),
})

/* ── Provider ──────────────────────────────────────────────────────────────── */

export function ScoreProvider({ children }: { children: React.ReactNode }) {
  const [scores, setScores] = useState<ScoreMap>(loadState)
  const activeRef = useRef<string | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Persist to sessionStorage on every change
  useEffect(() => { saveState(scores) }, [scores])

  // Timer: tick elapsed for the active challenge every second
  const startTimer = useCallback(() => {
    // Clear any existing interval first
    if (intervalRef.current) clearInterval(intervalRef.current)

    intervalRef.current = setInterval(() => {
      const id = activeRef.current
      if (!id) return

      setScores(prev => {
        const s = prev[id] ?? defaultState()
        if (s.solved) return prev // Don't tick if solved
        return { ...prev, [id]: { ...s, elapsedSeconds: s.elapsedSeconds + 1 } }
      })
    }, 1000)
  }, [])

  const stopTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  // Clean up on unmount
  useEffect(() => () => stopTimer(), [stopTimer])

  const setActiveChallenge = useCallback((id: string | null) => {
    activeRef.current = id
    if (id) {
      // Ensure state entry exists
      setScores(prev => {
        if (prev[id]) return prev
        return { ...prev, [id]: defaultState() }
      })
      startTimer()
    } else {
      stopTimer()
    }
  }, [startTimer, stopTimer])

  const incrementQueries = useCallback((id: string) => {
    setScores(prev => {
      const s = prev[id] ?? defaultState()
      if (s.solved) return prev // Don't increment if solved
      return { ...prev, [id]: { ...s, queryCount: s.queryCount + 1 } }
    })
  }, [])

  const submitChallengeFlag = useCallback(async (
    challengeId: string,
    flag: string
  ): Promise<{ success: boolean; score?: number; error?: string }> => {
    const sessionId = getSessionId()
    const state = scores[challengeId] ?? defaultState()

    try {
      const res = await submitFlag(
        sessionId,
        challengeId,
        flag,
        state.elapsedSeconds,
        state.queryCount
      )

      if (res.success && res.score !== undefined) {
        // Lock the score and mark solved
        setScores(prev => ({
          ...prev,
          [challengeId]: {
            ...prev[challengeId] ?? defaultState(),
            solved: true,
            lockedScore: res.score!,
          }
        }))
        return { success: true, score: res.score }
      }

      return { success: false, error: res.error || 'Incorrect flag.' }
    } catch (err: any) {
      const msg = err.response?.data?.error || err.message || 'Submission failed.'
      return { success: false, error: msg }
    }
  }, [scores])

  return (
    <Ctx.Provider value={{ scores, setActiveChallenge, incrementQueries, submitChallengeFlag }}>
      {children}
    </Ctx.Provider>
  )
}

export const useScore = () => useContext(Ctx)
