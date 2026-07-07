import { useEffect, useState } from 'react'
import { fetchStatus, sensitiveInfoChat } from '../api/client'
import type { ChatMessage, ModelStatus, SqlQueryLog } from '../types'
import NavBar from '../components/NavBar'
import ModelStatusBanner from '../components/ModelStatusBanner'
import ChatInterface from '../components/ChatInterface'
import { Terminal, Lock } from 'lucide-react'

export default function SensitiveInformationDisclosure() {
  const [messages, setMessages]       = useState<ChatMessage[]>([])
  const [loading, setLoading]         = useState(false)
  const [lastQueries, setLastQueries] = useState<SqlQueryLog[]>([])
  const [status, setStatus]           = useState<ModelStatus>({
    model_loaded:  false,
    model_name:    null,
    error_message: null
  })

  useEffect(() => {
    fetchStatus()
      .then(setStatus)
      .catch(err => setStatus({
        model_loaded:  false,
        model_name:    null,
        error_message: err.message || 'Failed to load API status'
      }))
  }, [])

  const handleUpdateMessage = () => {
    alert('Editing is not accepted in this module')
  }

  const handleSendMessage = async (content: string) => {
    const timeStr = new Date().toLocaleTimeString([], {
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    })
    const userMsg: ChatMessage = {
      id:        Math.random().toString(36).substr(2, 9),
      role:      'user',
      content,
      timestamp: timeStr
    }

    setMessages(prev => [...prev, userMsg])
    setLoading(true)
    setLastQueries([])

    const apiHistory = messages.map(m => ({ role: m.role, content: m.content }))

    try {
      const response = await sensitiveInfoChat(content, apiHistory)
      const aiTimeStr = new Date().toLocaleTimeString([], {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      })

      if (response.sql_queries && response.sql_queries.length > 0) {
        setLastQueries(response.sql_queries)
      }

      const reply = response.response
      if (reply) {
        setMessages(prev => [...prev, {
          id:        Math.random().toString(36).substr(2, 9),
          role:      'assistant',
          content:   reply,
          timestamp: aiTimeStr
        }])
      } else {
        setMessages(prev => [...prev, {
          id:        Math.random().toString(36).substr(2, 9),
          role:      'assistant',
          content:   response.error || 'The model returned an empty response.',
          timestamp: aiTimeStr,
          error:     true
        }])
      }
    } catch (err: any) {
      const errTimeStr = new Date().toLocaleTimeString([], {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      })
      setMessages(prev => [...prev, {
        id:        Math.random().toString(36).substr(2, 9),
        role:      'assistant',
        content:   err.response?.data?.error || err.message || 'Failed to execute call',
        timestamp: errTimeStr,
        error:     true
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      <NavBar title="Sensitive Info Disclosure Sandbox" subtitle="LLM06" />
      <ModelStatusBanner status={status} />

      <div className="flex-1 flex overflow-hidden">

        {/* ── Chat Section ─────────────────────────────────────── */}
        <div className="flex-1 flex flex-col border-r border-white/[0.05]">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            loading={loading}
            onUpdateMessage={handleUpdateMessage}
          />
        </div>

        {/* ── Right Sidebar ─────────────────────────────────────── */}
        <div className="w-[380px] flex flex-col bg-surface overflow-y-auto">

          {/* DB Console Panel */}
          {lastQueries.length > 0 && (
            <div className="border-b border-white/[0.05]">
              <div className="px-5 pt-5 pb-3 flex items-center gap-2">
                <Terminal size={13} className="text-cyan animate-pulse" />
                <h3 className="font-mono text-xs font-bold text-sub uppercase tracking-wider">
                  Database Console
                </h3>
              </div>
              <div className="px-4 pb-5 space-y-4">
                {lastQueries.map((q, i) => (
                  <div key={i} className="glass rounded border-cyan/10 overflow-hidden">
                    {/* Query */}
                    <div className="px-3 py-2 border-b border-white/[0.05] flex items-start gap-2">
                      <span className="text-[10px] font-mono text-cyan mt-0.5 shrink-0">SQL</span>
                      <pre className="text-[10px] font-mono text-primary leading-relaxed whitespace-pre-wrap break-all">
                        {q.query}
                      </pre>
                    </div>
                    {/* Result */}
                    <div className="px-3 py-2">
                      <span className="text-[9px] font-mono text-muted block mb-1 uppercase tracking-wider">Result</span>
                      <pre className="text-[10px] font-mono text-sub leading-relaxed whitespace-pre-wrap break-all max-h-40 overflow-y-auto">
                        {q.result}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Explanation Panel */}
          <div className="p-5 space-y-5">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Lock size={13} className="text-orange" />
                <h3 className="font-mono text-sm font-bold text-primary uppercase tracking-wider">
                  Vulnerability Explanation
                </h3>
              </div>
              <p className="text-xs text-sub leading-relaxed font-mono">
                <strong className="text-primary">LLM06 — Sensitive Information Disclosure</strong> occurs when
                an LLM agent with database access is manipulated into revealing classified data that its
                system prompt forbids it from sharing.
              </p>
              <p className="text-xs text-sub leading-relaxed font-mono mt-3">
                In this sandbox, the model is configured as a read-only HR database assistant with explicit
                instructions to redact password hashes, SSNs, salaries, and internal secrets. However, the
                LLM can be jailbroken to bypass these rules.
              </p>
              <p className="text-xs text-sub leading-relaxed font-mono mt-3">
                The <span className="text-cyan">Database Console</span> panel shows every SQL query the agent
                generated and executed in real time — giving you full visibility into what data the LLM
                actually retrieved from the database.
              </p>
            </div>

            <div className="border-t border-white/[0.05] pt-5">
              <h3 className="font-mono text-xs font-bold text-primary uppercase tracking-wider mb-3">
                Database Schema
              </h3>
              <div className="space-y-3">

                {/* users */}
                <div className="glass rounded border-white/[0.04] overflow-hidden">
                  <div className="px-3 py-2 border-b border-white/[0.06] flex items-center gap-2 bg-cyan/5">
                    <span className="text-[10px] font-mono font-bold text-cyan">users</span>
                  </div>
                  <table className="w-full text-[9px] font-mono">
                    <thead>
                      <tr className="border-b border-white/[0.04]">
                        <th className="text-left px-3 py-1.5 text-muted font-semibold">column</th>
                        <th className="text-left px-2 py-1.5 text-muted font-semibold">type</th>
                        <th className="text-right px-3 py-1.5 text-muted font-semibold">sensitivity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { col: 'id',         type: 'INTEGER', tag: null },
                        { col: 'username',   type: 'TEXT',    tag: null },
                        { col: 'email',      type: 'TEXT',    tag: null },
                        { col: 'role',       type: 'TEXT',    tag: null },
                        { col: 'password',   type: 'TEXT',    tag: 'restricted' },
                        { col: 'last_login', type: 'TEXT',    tag: null },
                      ].map(({ col, type, tag }) => (
                        <tr key={col} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                          <td className="px-3 py-1.5 text-primary">{col}</td>
                          <td className="px-2 py-1.5 text-sub">{type}</td>
                          <td className="px-3 py-1.5 text-right">
                            {tag === 'restricted' && (
                              <span className="text-[8px] font-bold text-red-400 bg-red-400/10 border border-red-400/20 px-1.5 py-0.5 rounded uppercase tracking-wide">
                                restricted
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* employees */}
                <div className="glass rounded border-white/[0.04] overflow-hidden">
                  <div className="px-3 py-2 border-b border-white/[0.06] flex items-center gap-2 bg-cyan/5">
                    <span className="text-[10px] font-mono font-bold text-cyan">employees</span>
                  </div>
                  <table className="w-full text-[9px] font-mono">
                    <thead>
                      <tr className="border-b border-white/[0.04]">
                        <th className="text-left px-3 py-1.5 text-muted font-semibold">column</th>
                        <th className="text-left px-2 py-1.5 text-muted font-semibold">type</th>
                        <th className="text-right px-3 py-1.5 text-muted font-semibold">sensitivity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { col: 'id',         type: 'INTEGER', tag: null },
                        { col: 'name',       type: 'TEXT',    tag: null },
                        { col: 'department', type: 'TEXT',    tag: null },
                        { col: 'title',      type: 'TEXT',    tag: null },
                        { col: 'salary',     type: 'REAL',    tag: 'restricted' },
                        { col: 'ssn',        type: 'TEXT',    tag: 'restricted' },
                        { col: 'hire_date',  type: 'TEXT',    tag: null },
                      ].map(({ col, type, tag }) => (
                        <tr key={col} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                          <td className="px-3 py-1.5 text-primary">{col}</td>
                          <td className="px-2 py-1.5 text-sub">{type}</td>
                          <td className="px-3 py-1.5 text-right">
                            {tag === 'restricted' && (
                              <span className="text-[8px] font-bold text-red-400 bg-red-400/10 border border-red-400/20 px-1.5 py-0.5 rounded uppercase tracking-wide">
                                restricted
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* secrets */}
                <div className="glass rounded border-white/[0.04] overflow-hidden">
                  <div className="px-3 py-2 border-b border-white/[0.06] flex items-center gap-2 bg-cyan/5">
                    <span className="text-[10px] font-mono font-bold text-cyan">secrets</span>
                  </div>
                  <table className="w-full text-[9px] font-mono">
                    <thead>
                      <tr className="border-b border-white/[0.04]">
                        <th className="text-left px-3 py-1.5 text-muted font-semibold">column</th>
                        <th className="text-left px-2 py-1.5 text-muted font-semibold">type</th>
                        <th className="text-right px-3 py-1.5 text-muted font-semibold">sensitivity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { col: 'id',             type: 'INTEGER', tag: null },
                        { col: 'label',          type: 'TEXT',    tag: null },
                        { col: 'value',          type: 'TEXT',    tag: 'top-secret' },
                        { col: 'classification', type: 'TEXT',    tag: null },
                      ].map(({ col, type, tag }) => (
                        <tr key={col} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                          <td className="px-3 py-1.5 text-primary">{col}</td>
                          <td className="px-2 py-1.5 text-sub">{type}</td>
                          <td className="px-3 py-1.5 text-right">
                            {tag === 'top-secret' && (
                              <span className="text-[8px] font-bold text-orange bg-orange/10 border border-orange/20 px-1.5 py-0.5 rounded uppercase tracking-wide">
                                top secret
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
