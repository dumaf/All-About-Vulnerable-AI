import { useState, useRef, useEffect } from 'react'
import { Send, Terminal, ShieldAlert } from 'lucide-react'
import type { ChatMessage, ContextChunk } from '../types'

interface ChatInterfaceProps {
  messages:     ChatMessage[]
  onSendMessage: (msg: string) => void
  loading:      boolean
}

export default function ChatInterface({ messages, onSendMessage, loading }: ChatInterfaceProps) {
  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    onSendMessage(input)
    setInput('')
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {/* ── Scroll Area ───────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8">
            <Terminal className="text-muted mb-4" size={40} />
            <p className="text-sub font-mono text-sm max-w-sm">
              Console interface active. Enter instructions below to communicate with the model.
            </p>
          </div>
        ) : (
          messages.map(msg => (
            <div
              key={msg.id}
              className={`flex flex-col gap-1 max-w-[85%] animate-fade-in ${
                msg.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'
              }`}
            >
              <div className="flex items-center gap-2 text-xs text-muted font-mono">
                <span>{msg.role === 'user' ? 'USER' : 'AI'}</span>
                <span>•</span>
                <span>{msg.timestamp}</span>
              </div>

              <div
                className={`px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  msg.role === 'user' ? 'bubble-user' : 'bubble-ai'
                } ${msg.error ? 'border-red/30 bg-red/5 text-red-400' : 'text-primary'}`}
              >
                {msg.content}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="flex flex-col gap-1 max-w-[85%] mr-auto items-start">
            <div className="flex items-center gap-2 text-xs text-muted font-mono">
              <span>AI</span>
              <span>•</span>
              <span className="italic">thinking</span>
            </div>
            <div className="bubble-ai px-4 py-3 flex items-center gap-1.5 h-10 w-20 justify-center">
              <span className="w-1.5 h-1.5 bg-cyan rounded-full dot-1" />
              <span className="w-1.5 h-1.5 bg-cyan rounded-full dot-2" />
              <span className="w-1.5 h-1.5 bg-cyan rounded-full dot-3" />
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* ── Input panel ──────────────────────────────────────────────────────── */}
      <form onSubmit={submit} className="p-4 glass border-t border-white/[0.08] flex gap-3">
        <input
          id="chat-input-box"
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={loading ? 'Processing execution...' : 'Enter prompt or instruction...'}
          disabled={loading}
          autoFocus
          className="flex-1 bg-white/5 border border-white/10 px-4 py-3 text-sm text-primary placeholder:text-muted focus:outline-none focus:border-cyan transition-colors font-mono disabled:opacity-50"
        />
        <button
          id="chat-send-btn"
          type="submit"
          disabled={!input.trim() || loading}
          className="bg-cyan/10 hover:bg-cyan/20 border border-cyan/35 text-cyan hover:text-white px-5 py-3 flex items-center justify-center transition-all disabled:opacity-50 disabled:bg-transparent disabled:border-white/10 disabled:text-muted"
        >
          <Send size={15} />
        </button>
      </form>
    </div>
  )
}
