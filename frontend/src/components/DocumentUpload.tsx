import { useState, useRef } from 'react'
import { Upload, Trash2, FileText, Loader2 } from 'lucide-react'
import type { Document } from '../types'

interface DocumentUploadProps {
  documents:         Document[]
  onUpload:          (file: File) => Promise<void>
  onDelete:          (name: string) => Promise<void>
  refreshDocuments: () => void
}

export default function DocumentUpload({ documents, onUpload, onDelete, refreshDocuments }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await processFile(e.target.files[0])
    }
  }

  const processFile = async (file: File) => {
    setError(null)
    setUploading(true)
    try {
      await onUpload(file)
      refreshDocuments()
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || "Failed to upload file")
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="w-80 border-r border-white/[0.08] flex flex-col h-full bg-white/[0.01]">
      <div className="p-4 border-b border-white/[0.08]">
        <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-sub">Document Store</h3>
        <p className="text-[11px] text-muted font-mono mt-0.5">Ingest reference sources for the RAG index.</p>
      </div>

      {/* Drag & Drop Area */}
      <div className="p-4 border-b border-white/[0.08]">
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border border-dashed p-6 text-center cursor-pointer transition-colors flex flex-col items-center justify-center min-h-[120px] ${
            dragActive ? 'border-cyan bg-cyan/5' : 'border-white/10 hover:border-white/20'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileChange}
            className="hidden"
          />
          {uploading ? (
            <>
              <Loader2 className="animate-spin text-cyan mb-2" size={24} />
              <span className="text-xs text-cyan font-mono">Indexing document...</span>
            </>
          ) : (
            <>
              <Upload className="text-muted mb-2" size={20} />
              <span className="text-xs text-primary font-mono block">Drop PDF or TXT here</span>
              <span className="text-[10px] text-muted font-mono mt-1">or click to browse</span>
            </>
          )}
        </div>

        {error && (
          <p className="text-[10px] text-red-400 font-mono mt-2 leading-relaxed bg-red-950/20 border border-red-900/30 p-2">
            Error: {error}
          </p>
        )}
      </div>

      {/* Document Inventory */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <div className="flex items-center justify-between text-[11px] text-muted font-mono">
          <span>INDEXED FILES ({documents.length})</span>
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-8 text-muted font-mono text-[11px]">
            No source documents uploaded.
          </div>
        ) : (
          <div className="space-y-2">
            {documents.map((doc, idx) => (
              <div key={idx} className="glass p-3 flex items-start justify-between gap-3 group">
                <FileText size={15} className="text-cyan shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0 font-mono text-[11px]">
                  <p className="text-primary truncate font-medium" title={doc.name}>
                    {doc.name}
                  </p>
                  <p className="text-[9px] text-muted mt-0.5">
                    {(doc.size / 1024).toFixed(1)} KB • {doc.chunks} chunks
                  </p>
                </div>
                <button
                  onClick={() => onDelete(doc.name)}
                  className="text-muted hover:text-red transition-colors shrink-0"
                  title="Remove from vector store"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
