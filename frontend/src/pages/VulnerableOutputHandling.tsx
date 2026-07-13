import { useEffect, useState, useCallback } from 'react'
import { outputHandlingChat, fetchStatus } from '../api/client'
import type { ChatMessage, ModelStatus } from '../types'
import NavBar from '../components/NavBar'
import ModelStatusBanner from '../components/ModelStatusBanner'
import ChatInterface from '../components/ChatInterface'
import ScoringPanel from '../components/ScoringPanel'
import { useScore } from '../context/ScoreContext'
import { Lock, Flag, CheckCircle2 } from 'lucide-react'

const CHALLENGE_ID = 'output-handling'

declare global {
  interface Window {
    markChallengeComplete?: (flag: string) => void
  }
}

export default function VulnerableOutputHandling() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [challengeComplete, setChallengeComplete] = useState(false)
  const [capturedFlag, setCapturedFlag] = useState<string | null>(null)
  const [status, setStatus] = useState<ModelStatus>({
    model_loaded: false,
    model_name: null,
    error_message: null
  })
  const { setActiveChallenge, incrementQueries } = useScore()

  useEffect(() => {
    setActiveChallenge(CHALLENGE_ID)
    return () => setActiveChallenge(null)
  }, [setActiveChallenge])

  // Expose the global callback that the XSS payload will call
  const handleChallengeComplete = useCallback((flag: string) => {
    if (flag && flag.startsWith('FLAG{')) {
      setChallengeComplete(true)
      setCapturedFlag(flag)
    }
  }, [])

  useEffect(() => {
    window.markChallengeComplete = handleChallengeComplete
    return () => {
      delete window.markChallengeComplete
    }
  }, [handleChallengeComplete])

  useEffect(() => {
    fetchStatus()
      .then(setStatus)
      .catch(err => setStatus({
        model_loaded: false,
        model_name: null,
        error_message: err.message || "Failed to load API status"
      }))
  }, [])

  const handleUpdateMessage = (id: string, newContent: string) => {
    alert("Editing is not accepted in this module");
  }

  const handleSendMessage = async (content: string) => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    const userMsg: ChatMessage = {
      id: Math.random().toString(36).substr(2, 9),
      role: 'user',
      content,
      timestamp: timeStr
    }

    setMessages(prev => [...prev, userMsg])
    setLoading(true)
    incrementQueries(CHALLENGE_ID)

    const apiHistory = messages.map(m => ({
      role: m.role,
      content: m.content
    }))

    try {
      const response = await outputHandlingChat(content, apiHistory)
      const aiTimeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

      const reply = response.response
      if (reply) {
        setMessages(prev => [...prev, {
          id: Math.random().toString(36).substr(2, 9),
          role: 'assistant',
          content: reply,
          timestamp: aiTimeStr
        }])
      } else {
        setMessages(prev => [...prev, {
          id: Math.random().toString(36).substr(2, 9),
          role: 'assistant',
          content: response.error || "Execution returned an empty response.",
          timestamp: aiTimeStr,
          error: true
        }])
      }
    } catch (err: any) {
      const errTimeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      setMessages(prev => [...prev, {
        id: Math.random().toString(36).substr(2, 9),
        role: 'assistant',
        content: err.response?.data?.error || err.message || "Failed to execute call",
        timestamp: errTimeStr,
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      <NavBar title="Vulnerable Output Handling" subtitle="XSS via LLM Output" />
      <ModelStatusBanner status={status} />

      {/* Challenge completion banner */}
      {challengeComplete && (
        <div className="bg-green/10 border-b border-green/30 px-6 py-3 flex items-center gap-3 animate-fade-in">
          <CheckCircle2 size={18} className="text-green" />
          <div className="font-mono text-sm">
            <span className="text-green font-bold">Challenge Complete!</span>
            <span className="text-sub ml-3">Flag captured: </span>
            <code className="text-primary bg-white/5 px-2 py-0.5 border border-white/10">{capturedFlag}</code>
          </div>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        {/* Chat Section — renders HTML unsafely */}
        <div className="flex-1 flex flex-col border-r border-white/[0.05]">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            loading={loading}
            onUpdateMessage={handleUpdateMessage}
            renderUnsafeHtml={true}
          />
        </div>

        {/* ── Right Sidebar ─────────────────────────────────────── */}
        <div className="w-[380px] flex flex-col bg-surface overflow-y-auto">
          <ScoringPanel challengeId={CHALLENGE_ID} />

          {/* Vulnerability Explanation */}
          <div className="p-5 space-y-5">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Lock size={13} className="text-orange" />
                <h3 className="font-mono text-sm font-bold text-primary uppercase tracking-wider">
                  Vulnerability Explanation
                </h3>
              </div>
              <p className="text-xs text-sub leading-relaxed font-mono">
                <strong className="text-primary">LLM02 — Insecure Output Handling</strong> occurs when an
                application renders LLM-generated content without sanitization. If the model produces HTML
                containing JavaScript, and the frontend blindly injects it via <code className="text-cyan">dangerouslySetInnerHTML</code>,
                the script executes in the user's browser context.
              </p>
              <p className="text-xs text-sub leading-relaxed font-mono mt-3">
                In this sandbox, the AI assistant is configured to output raw HTML. The frontend deliberately
                renders assistant responses as unsanitized HTML — creating a cross-site scripting (XSS) surface.
              </p>
              <p className="text-xs text-sub leading-relaxed font-mono mt-3">
                Your goal: convince the model to produce HTML with a JavaScript payload that fetches the flag
                from <code className="text-cyan">/api/internal/flag</code> and calls{' '}
                <code className="text-cyan">window.markChallengeComplete(flag)</code>.
              </p>
            </div>

            {/* Challenge Objective */}
            <div className="border-t border-white/[0.05] pt-5">
              <div className="flex items-center gap-2 mb-3">
                <Flag size={13} className="text-cyan" />
                <h3 className="font-mono text-sm font-bold text-primary uppercase tracking-wider">
                  Challenge Objective
                </h3>
              </div>
              <div className="space-y-2">
                <div className="flex items-start gap-2 text-xs font-mono text-sub">
                  <span className="text-muted shrink-0 mt-px">1.</span>
                  <span>Convince the AI to generate HTML containing a <code className="text-cyan">&lt;script&gt;</code> or event-handler payload.</span>
                </div>
                <div className="flex items-start gap-2 text-xs font-mono text-sub">
                  <span className="text-muted shrink-0 mt-px">2.</span>
                  <span>The payload should fetch <code className="text-cyan">/api/internal/flag</code> (same-origin GET).</span>
                </div>
                <div className="flex items-start gap-2 text-xs font-mono text-sub">
                  <span className="text-muted shrink-0 mt-px">3.</span>
                  <span>Extract the <code className="text-cyan">flag</code> field from the JSON response.</span>
                </div>
                <div className="flex items-start gap-2 text-xs font-mono text-sub">
                  <span className="text-muted shrink-0 mt-px">4.</span>
                  <span>Call <code className="text-cyan">window.markChallengeComplete(flag)</code> to complete the challenge.</span>
                </div>
              </div>

              {/* Challenge status indicator */}
              <div className={`mt-4 p-3 border font-mono text-xs flex items-center gap-2 ${
                challengeComplete
                  ? 'border-green/30 bg-green/5 text-green'
                  : 'border-white/10 bg-white/[0.02] text-muted'
              }`}>
                {challengeComplete ? (
                  <>
                    <CheckCircle2 size={14} />
                    <span className="font-bold">FLAG CAPTURED</span>
                  </>
                ) : (
                  <>
                    <Flag size={14} />
                    <span>Awaiting payload execution…</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
