import { useEffect, useState } from 'react'
import { promptInjectionChat, fetchStatus } from '../api/client'
import type { ChatMessage, ModelStatus } from '../types'
import NavBar from '../components/NavBar'
import ModelStatusBanner from '../components/ModelStatusBanner'
import ChatInterface from '../components/ChatInterface'

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
      <ChatInterface
        messages={messages}
        onSendMessage={handleSendMessage}
        loading={loading}
      />
    </div>
  )
}
