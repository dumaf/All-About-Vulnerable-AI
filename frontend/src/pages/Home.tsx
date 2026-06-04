import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ShieldAlert, Database, HelpCircle, Sun, Moon } from 'lucide-react'
import { fetchStatus } from '../api/client'
import { useTheme } from '../context/ThemeContext'
import ModelStatusBanner from '../components/ModelStatusBanner'
import type { ModelStatus } from '../types'

export default function Home() {
  const navigate = useNavigate()
  const { theme, toggle } = useTheme()
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
        error_message: err.message || "Failed to contact API server"
      }))
  }, [])

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {/* Header bar */}
      <header className="flex items-center gap-4 px-6 py-4 glass border-b border-white/[0.08]">
        <div className="flex items-center gap-2">
          <ShieldAlert size={20} className="text-orange" />
          <h1 className="font-mono text-base font-bold tracking-wider uppercase text-primary">AAVAI</h1>
          <span className="text-xs text-muted font-mono hidden md:inline">| All About Vulnerable AI</span>
        </div>

        <button
          id="home-theme-toggle"
          onClick={toggle}
          className="ml-auto text-muted hover:text-primary transition-colors"
          title="Toggle light/dark layout"
        >
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </header>

      {/* Model status bar */}
      <ModelStatusBanner status={status} />

      {/* Dashboard options container */}
      <main className="flex-1 overflow-y-auto p-6 md:p-12 max-w-5xl w-full mx-auto flex flex-col justify-center">
        <div className="mb-12 max-w-2xl">
          <h2 className="font-mono text-2xl font-semibold mb-3 tracking-tight">AI Vulnerabilities Lab</h2>
          <p className="text-sm text-sub leading-relaxed font-mono">
            Learn and test security mechanics in AI LLM systems. Select a sandbox module below to interact with local hardware boundaries.
          </p>
        </div>

        {/* Challenge Cards Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          
          {/* Prompt Injection Card */}
          <div
            id="prompt-injection-card"
            onClick={() => navigate('/prompt-injection')}
            className="module-card glass cursor-pointer p-6 hover:border-orange/40 transition-all flex flex-col justify-between group"
          >
            <div>
              <div className="w-10 h-10 bg-orange/10 border border-orange/20 flex items-center justify-center text-orange mb-5 group-hover:bg-orange/20 transition-colors">
                <ShieldAlert size={20} />
              </div>
              <h3 className="font-mono text-base font-bold mb-2 text-primary">Prompt Injection</h3>
              <p className="text-xs text-sub leading-relaxed font-mono">
                Bypass system constraints and retrieve administrative keys. Test system prompts against direct overrides.
              </p>
            </div>
            <div className="mt-8 flex items-center gap-1 text-[11px] font-mono text-orange uppercase tracking-wider font-semibold">
              Enter Module &rarr;
            </div>
          </div>

          {/* RAG Poisoning Card */}
          <div
            id="rag-poisoning-card"
            onClick={() => navigate('/rag-poisoning')}
            className="module-card glass cursor-pointer p-6 hover:border-cyan/40 transition-all flex flex-col justify-between group"
          >
            <div>
              <div className="w-10 h-10 bg-cyan/10 border border-cyan/20 flex items-center justify-center text-cyan mb-5 group-hover:bg-cyan/20 transition-colors">
                <Database size={20} />
              </div>
              <h3 className="font-mono text-base font-bold mb-2 text-primary">RAG Poisoning</h3>
              <p className="text-xs text-sub leading-relaxed font-mono">
                Inject poisoned data into semantic document stores. Manipulate system actions using untrusted retrievals.
              </p>
            </div>
            <div className="mt-8 flex items-center gap-1 text-[11px] font-mono text-cyan uppercase tracking-wider font-semibold">
              Enter Module &rarr;
            </div>
          </div>

        </div>

        {/* Footer notes */}
        <footer className="flex items-center gap-4 text-[10px] text-muted font-mono mt-auto border-t border-white/[0.05] pt-6">
          <span>PLATFORM: v1.0.0</span>
          <span>•</span>
          <span>HARDWARE: LOCAL CPU/GPU</span>
          <span className="ml-auto flex items-center gap-1 hover:text-primary transition-colors cursor-help">
            <HelpCircle size={11} />
            Security Sandbox
          </span>
        </footer>
      </main>
    </div>
  )
}
