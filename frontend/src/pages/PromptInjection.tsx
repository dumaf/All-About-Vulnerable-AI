import { useEffect, useState } from 'react'
import { promptInjectionChat, fetchStatus } from '../api/client'
import type { ChatMessage, ModelStatus } from '../types'
import NavBar from '../components/NavBar'
import ModelStatusBanner from '../components/ModelStatusBanner'
import ChatInterface from '../components/ChatInterface'
import { Lock } from 'lucide-react'

export default function PromptInjection() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<ModelStatus>({
    model_loaded: false,
    model_name: null,
    error_message: null
  })

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

    // Build plain message objects required by Python backend API client
    const apiHistory = messages.map(m => ({
      role: m.role,
      content: m.content
    }))

    try {
      const response = await promptInjectionChat(content, apiHistory)
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
      <NavBar title="Prompt Injection Sandbox" subtitle="Direct Override" />
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

        {/* ── Right Sidebar ─────────────────────────────────────── */}
        <div className="w-[380px] flex flex-col bg-surface overflow-y-auto p-5 space-y-5">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Lock size={13} className="text-orange" />
              <h3 className="font-mono text-sm font-bold text-primary uppercase tracking-wider">
                Vulnerability Explanation
              </h3>
            </div>
            <p className="text-xs text-sub leading-relaxed font-mono">
              <strong className="text-primary">LLM01 — Prompt Injection</strong> occurs when a user uses crafted prompts to override the system instructions of the LLM. This can lead to unauthorized actions, safety guardrail bypasses, or administrative privilege escalations.
            </p>
            <p className="text-xs text-sub leading-relaxed font-mono mt-3">
              In this sandbox, the model is guided by a system prompt instructing it to never disclose administrative keys or secret values.
            </p>
            <p className="text-xs text-sub leading-relaxed font-mono mt-3">
              Try bypass strategies like roleplay, translations, reverse psychology, or directly ordering the agent to ignore previous instructions to reveal the protected flags.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
