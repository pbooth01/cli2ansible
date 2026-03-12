/**
 * API client for cli2ansible backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

// ============ Types ============

export interface CastFile {
  id: string
  session_id: string
  file_name: string
  file_size: number
  uploaded_at: string
}

export interface Session {
  id: string
  name: string
  status: string
  created_at: string
  updated_at: string
  metadata: Record<string, any>
  cast_file?: CastFile | null
}

export interface MostCommonCommand {
  command: string
  count: number
}

export interface Report {
  session_id: string
  total_commands: number
  high_confidence: number
  medium_confidence: number
  low_confidence: number
  skipped_commands: number
  sudo_command_count: number
  session_duration_seconds: number
  module_breakdown: Record<string, number>
  most_common_commands: MostCommonCommand[]
  warnings: string[]
}

// ============ API Functions ============

/**
 * Create a new session
 */
export async function createSession(
  name: string,
  metadata: Record<string, any> = {}
): Promise<Session> {
  const response = await fetch(`${API_BASE_URL}/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, metadata }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to create session' }))
    throw new Error(error.detail || 'Failed to create session')
  }

  return response.json()
}

/**
 * List all sessions
 */
export async function listSessions(): Promise<Session[]> {
  const response = await fetch(`${API_BASE_URL}/sessions`)

  if (!response.ok) {
    throw new Error('Failed to fetch sessions')
  }

  const data = await response.json()
  return data.sessions || []
}

/**
 * Get a session by ID
 */
export async function getSession(sessionId: string): Promise<Session> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Session not found' }))
    throw new Error(error.detail || 'Session not found')
  }

  return response.json()
}

/**
 * Delete a session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to delete session' }))
    throw new Error(error.detail || 'Failed to delete session')
  }
}

/**
 * Upload a .cast file to a session
 */
export async function uploadCastFile(sessionId: string, file: File): Promise<void> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/cast`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to upload file' }))
    throw new Error(error.detail || 'Failed to upload file')
  }
}

/**
 * Compile a session to Ansible playbook
 */
export async function compileSession(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/compile`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to compile session' }))
    throw new Error(error.detail || 'Failed to compile session')
  }
}

/**
 * Get compilation report for a session
 */
export async function getReport(sessionId: string): Promise<Report> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/report`)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch report' }))
    throw new Error(error.detail || 'Failed to fetch report')
  }

  return response.json()
}

/**
 * Download the compiled playbook as a zip file
 */
export async function downloadPlaybook(sessionId: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/playbook`)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to download playbook' }))
    throw new Error(error.detail || 'Failed to download playbook')
  }

  return response.text()
}

