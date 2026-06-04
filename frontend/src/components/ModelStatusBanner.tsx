import { AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react'
import type { ModelStatus } from '../types'

interface ModelStatusBannerProps {
  status: ModelStatus
}

export default function ModelStatusBanner({ status }: ModelStatusBannerProps) {
  if (status.model_loaded) {
    return (
      <div id="model-status" className="flex items-center gap-3 px-4 py-2 border-b border-green/20 bg-green/5 text-xs text-green font-mono">
        <CheckCircle size={13} />
        <span>Loaded: <strong className="font-semibold">{status.model_name}</strong></span>
        <div className="w-1.5 h-1.5 bg-green rounded-full animate-ping ml-auto" />
      </div>
    )
  }

  if (status.error_message) {
    return (
      <div id="model-status" className="flex flex-col gap-1 px-4 py-3 border-b border-orange/20 bg-orange/5 text-xs text-orange font-mono">
        <div className="flex items-center gap-2 font-semibold">
          <AlertTriangle size={14} />
          <span>Llama model could not be loaded dynamically. Running in Model-less mode.</span>
        </div>
        <p className="opacity-80 leading-relaxed max-w-2xl">{status.error_message}</p>
      </div>
    )
  }

  return (
    <div id="model-status" className="flex items-center gap-3 px-4 py-2 border-b border-cyan/25 bg-cyan/5 text-xs text-cyan font-mono animate-pulse-slow">
      <RefreshCw size={13} className="animate-spin" />
      <span>Loading local LLM background thread...</span>
    </div>
  )
}
