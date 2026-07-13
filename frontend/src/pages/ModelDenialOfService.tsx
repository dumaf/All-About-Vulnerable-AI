import { useEffect, useState } from 'react'
import { dosChat, fetchDosStatus } from '../api/client'
import type { ChatMessage, ModelStatus } from '../types'
import NavBar from '../components/NavBar'
import ModelStatusBanner from '../components/ModelStatusBanner'
import ChatInterface from '../components/ChatInterface'
import ScoringPanel from '../components/ScoringPanel'
import { useScore } from '../context/ScoreContext'
import { CheckCircle, AlertTriangle, ShieldAlert } from 'lucide-react'

const CHALLENGE_ID = 'model-dos'

export default function ModelDenialOfService() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<ModelStatus>({
    model_loaded: false,
    model_name: null,
    error_message: null,
    rate: 0,
    available: true
  })
  const { setActiveChallenge, incrementQueries } = useScore()

  useEffect(() => {
    setActiveChallenge(CHALLENGE_ID)
    return () => setActiveChallenge(null)
  }, [setActiveChallenge])

  // Poll status every 1 second to update live rate and availability state
  useEffect(() => {
    const getStatus = () => {
      fetchDosStatus()
        .then(setStatus)
        .catch(err => setStatus({
          model_loaded: false,
          model_name: null,
          error_message: err.message || "Failed to load DoS API status",
          rate: 0,
          available: false
        }))
    }

    getStatus()
    const interval = setInterval(getStatus, 1000)
    return () => clearInterval(interval)
  }, [])

  const handleUpdateMessage = () => {
    alert("Editing is not accepted in this module")
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
      const response = await dosChat(content, apiHistory)
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

  const rate = status.rate ?? 0
  const isAvailable = status.available !== false
  const ratePercentage = Math.min(100, (rate / 50) * 100)

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      <NavBar title="Model Denial of Service Sandbox" subtitle="Rate Limiting" available={isAvailable} />
      <ModelStatusBanner status={status} />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Section */}
        <div className="flex-1 flex flex-col border-r border-white/[0.05]">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            loading={loading}
            onUpdateMessage={handleUpdateMessage}
          />
        </div>

        {/* Sidebar Info Section */}
        <div className="w-[380px] flex flex-col bg-surface overflow-y-auto">
          <ScoringPanel challengeId={CHALLENGE_ID} />

          <div className="p-6 space-y-6">
            <div>
              <h3 className="font-mono text-sm font-bold text-primary mb-3 uppercase tracking-wider">
                Vulnerability Explanation
              </h3>
              <p className="text-xs text-sub leading-relaxed font-mono">
                Large Language Models are computationally heavy. Serving an LLM request requires high GPU memory and compute processing.
              </p>
              <p className="text-xs text-sub leading-relaxed font-mono mt-3">
                If an attacker floods the inference engine with high-frequency queries, it causes resource exhaustion, resulting in high latency, out-of-memory errors, or service crash.
              </p>
              <p className="text-xs text-sub leading-relaxed font-mono mt-3">
                This sandbox is rate-limited to <strong>50 requests per second</strong> on an isolated port. Exceeding this rate simulates service failure, shutting down the chatbot temporarily.
              </p>
            </div>

            <div className="border-t border-white/[0.05] pt-6">
              <h3 className="font-mono text-sm font-bold text-primary mb-4 uppercase tracking-wider">
                Live Metrics (Port 5001)
              </h3>
              
              <div className="space-y-4">
                {/* Availability Info */}
                <div className="flex items-center justify-between p-3 glass rounded border border-white/[0.04]">
                  <span className="text-xs text-muted font-mono">Availability State:</span>
                  <div className="flex items-center gap-2">
                    {isAvailable ? (
                      <>
                        <CheckCircle size={14} className="text-green" />
                        <span className="text-xs text-green font-mono font-bold">ONLINE</span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle size={14} className="text-red-400" />
                        <span className="text-xs text-red-400 font-mono font-bold">OFFLINE</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Request Rate Gauge */}
                <div className="p-3 glass rounded border border-white/[0.04] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted font-mono">Request Rate:</span>
                    <span className="text-xs font-mono font-bold text-primary">{rate} / 50 req/s</span>
                  </div>
                  <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        ratePercentage >= 90 ? 'bg-red' : ratePercentage >= 50 ? 'bg-orange' : 'bg-green'
                      }`}
                      style={{ width: `${ratePercentage}%` }}
                    />
                  </div>
                </div>
                
                {/* Alert Message when Down */}
                {!isAvailable && (
                  <div className="p-3 bg-red/10 border border-red/20 rounded text-xs text-red-400 font-mono leading-relaxed flex gap-2">
                    <ShieldAlert size={16} className="shrink-0 mt-0.5" />
                    <div>
                      <strong className="font-semibold block mb-0.5">DoS Condition Triggered</strong>
                      The system has received too many requests. The model will remain offline for a short cooldown period.
                      {status.flag && (
                        <div className="mt-2 p-2 bg-green/10 border border-green/20 rounded text-green">
                          <strong>Flag captured:</strong>{' '}
                          <code className="bg-white/5 px-1.5 py-0.5 border border-white/10">{status.flag}</code>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
