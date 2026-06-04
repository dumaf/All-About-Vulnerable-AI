import axios from 'axios'
import type { ModelStatus, ChatResponse, UploadResponse, Document } from '../types'

const api = axios.create({ baseURL: '/api' })

export async function fetchStatus(): Promise<ModelStatus> {
  const { data } = await api.get('/status')
  return data
}

export async function promptInjectionChat(
  message: string,
  history: { role: string; content: string }[]
): Promise<ChatResponse> {
  const { data } = await api.post('/prompt-injection/chat', { message, history })
  return data
}

export async function ragChat(
  message: string,
  history: { role: string; content: string }[]
): Promise<ChatResponse> {
  const { data } = await api.post('/rag-poisoning/chat', { message, history })
  return data
}

export async function uploadDocument(
  file: File,
  onProgress?: (pct: number) => void
): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/rag-poisoning/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: e => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100))
    },
  })
  return data
}

export async function fetchDocuments(): Promise<Document[]> {
  const { data } = await api.get('/rag-poisoning/documents')
  return data.documents ?? []
}

export async function deleteDocument(name: string): Promise<void> {
  await api.delete(`/rag-poisoning/documents/${encodeURIComponent(name)}`)
}
