export interface ChatMessage {
  id:        string
  role:      'user' | 'assistant'
  content:   string
  timestamp: string
  error?:    boolean
}

export interface ModelStatus {
  model_loaded:  boolean
  model_name:    string | null
  error_message: string | null
  rate?:         number
  available?:    boolean
  flag?:         string
}

export interface Document {
  name:        string
  size:        number
  uploaded_at: string
  chunks:      number
}

export interface ContextChunk {
  doc_name:    string
  content:     string
  chunk_index: number
}

export interface SqlQueryLog {
  query:  string
  result: string
}

export interface ChatResponse {
  response:        string | null
  model_available: boolean
  error?:          string
  context_used?:   ContextChunk[]
  sql_queries?:    SqlQueryLog[]
}

export interface UploadResponse {
  success:        boolean
  filename:       string
  chunks_indexed: number
  error?:         string
}

export interface ChallengeScoreState {
  elapsedSeconds: number
  queryCount:     number
  solved:         boolean
  lockedScore:    number | null
}

export interface ScoreSubmissionResponse {
  success: boolean
  score?:  number
  error?:  string
}
