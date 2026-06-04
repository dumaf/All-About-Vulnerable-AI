import { useEffect, useState } from 'react'
import { fetchDocuments, uploadDocument, deleteDocument, ragChat, fetchStatus } from '../api/client'
import type { ChatMessage, Document, ModelStatus, ContextChunk } from '../types'
import NavBar from '../components/NavBar'
import ModelStatusBanner from '../components/ModelStatusBanner'
import DocumentUpload from '../components/DocumentUpload'
import ChatInterface from '../components/ChatInterface'
import { Database, FileText } from 'lucide-react'

export default function RagPoisoning() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [lastContext, setLastContext] = useState<ContextChunk[]>([])
  const [status, setStatus] = useState<ModelStatus>({
    model_loaded: false,
    model_name: null,
    error_message: null
  })

  const loadData = () => {
    fetchDocuments().then(setDocuments).catch(console.error)
  }

  useEffect(() => {
    loadData()
    fetchStatus()
      .then(setStatus)
      .catch(err => setStatus({
        model_loaded: false,
        model_name: null,
        error_message: err.message || "Failed to load API status"
      }))
  }, [])

  const handleUpload = async (file: File) => {
    await uploadDocument(file)
  }

  const handleDelete = async (name: string) => {
    await deleteDocument(name)
    loadData()
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
    setLastContext([])

    const apiHistory = messages.map(m => ({
      role: m.role,
      content: m.content
    }))

    try {
      const response = await ragChat(content, apiHistory)
      const aiTimeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

      if (response.context_used) {
        setLastContext(response.context_used)
      }

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
      <NavBar title="RAG Poisoning Sandbox" subtitle="Semantic Injection" />
      <ModelStatusBanner status={status} />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar uploader */}
        <DocumentUpload
          documents={documents}
          onUpload={handleUpload}
          onDelete={handleDelete}
          refreshDocuments={loadData}
        />

        {/* Chat area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            loading={loading}
          />
        </div>

        {/* Context inspector sidebar */}
        {lastContext.length > 0 && (
          <div className="w-80 border-l border-white/[0.08] flex flex-col h-full bg-white/[0.01]">
            <div className="p-4 border-b border-white/[0.08] flex items-center gap-2">
              <Database size={14} className="text-cyan animate-pulse" />
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-sub">Retrieved Chunks</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {lastContext.map((c, i) => (
                <div key={i} className="glass p-3 font-mono text-[10px] space-y-2 border-cyan/20">
                  <div className="flex items-center justify-between text-muted border-b border-white/[0.05] pb-1.5">
                    <span className="flex items-center gap-1">
                      <FileText size={10} />
                      {c.doc_name}
                    </span>
                    <span>idx: {c.chunk_index}</span>
                  </div>
                  <p className="text-primary leading-relaxed">{c.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
