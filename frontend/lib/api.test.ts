/**
 * Tests for API client functions
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import {
  createSession,
  listSessions,
  getSession,
  deleteSession,
  uploadCastFile,
  compileSession,
  getReport,
  downloadPlaybook,
} from './api'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('API Client', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('createSession', () => {
    it('should create a session successfully', async () => {
      const mockSession = {
        id: 'test-id',
        name: 'Test Session',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        metadata: {},
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await createSession('Test Session', { key: 'value' })

      expect(result).toEqual(mockSession)
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'Test Session', metadata: { key: 'value' } }),
      })
    })

    it('should handle creation errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Session creation failed' }),
      })

      await expect(createSession('Test')).rejects.toThrow('Session creation failed')
    })

    it('should handle network errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => {
          throw new Error('Network error')
        },
      })

      await expect(createSession('Test')).rejects.toThrow('Failed to create session')
    })
  })

  describe('listSessions', () => {
    it('should list all sessions', async () => {
      const mockSessions = [
        { id: '1', name: 'Session 1', status: 'active', created_at: '', updated_at: '', metadata: {} },
        { id: '2', name: 'Session 2', status: 'active', created_at: '', updated_at: '', metadata: {} },
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ sessions: mockSessions }),
      })

      const result = await listSessions()

      expect(result).toEqual(mockSessions)
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/sessions')
    })

    it('should return empty array if sessions key is missing', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      })

      const result = await listSessions()

      expect(result).toEqual([])
    })

    it('should handle fetch errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
      })

      await expect(listSessions()).rejects.toThrow('Failed to fetch sessions')
    })
  })

  describe('getSession', () => {
    it('should get a session by ID', async () => {
      const mockSession = {
        id: 'test-id',
        name: 'Test Session',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        metadata: {},
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await getSession('test-id')

      expect(result).toEqual(mockSession)
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/sessions/test-id')
    })

    it('should handle not found errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Session not found' }),
      })

      await expect(getSession('invalid-id')).rejects.toThrow('Session not found')
    })
  })




  describe('deleteSession', () => {
    it('should delete a session successfully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
      })

      await deleteSession('test-id')

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/sessions/test-id', {
        method: 'DELETE',
      })
    })

    it('should handle deletion errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Failed to delete' }),
      })

      await expect(deleteSession('test-id')).rejects.toThrow('Failed to delete')
    })
  })

  describe('uploadCastFile', () => {
    it('should upload a cast file successfully', async () => {
      const mockFile = new File(['test content'], 'test.cast', { type: 'application/octet-stream' })

      mockFetch.mockResolvedValueOnce({
        ok: true,
      })

      await uploadCastFile('session-id', mockFile)

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/sessions/session-id/cast',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        })
      )
    })

    it('should handle upload errors', async () => {
      const mockFile = new File(['test'], 'test.cast', { type: 'application/octet-stream' })

      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Upload failed' }),
      })

      await expect(uploadCastFile('session-id', mockFile)).rejects.toThrow('Upload failed')
    })
  })

  describe('compileSession', () => {
    it('should compile a session successfully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
      })

      await compileSession('session-id')

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/sessions/session-id/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })
    })

    it('should handle compilation errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Compilation failed' }),
      })

      await expect(compileSession('session-id')).rejects.toThrow('Compilation failed')
    })
  })

  describe('getReport', () => {
    it('should get a compilation report', async () => {
      const mockReport = {
        session_id: 'test-id',
        total_commands: 10,
        high_confidence: 8,
        medium_confidence: 2,
        low_confidence: 0,
        skipped_commands: 0,
        sudo_command_count: 3,
        session_duration_seconds: 120,
        module_breakdown: { apt: 5, copy: 3 },
        most_common_commands: [{ command: 'apt install', count: 5 }],
        warnings: [],
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockReport,
      })

      const result = await getReport('test-id')

      expect(result).toEqual(mockReport)
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/sessions/test-id/report')
    })

    it('should handle report fetch errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Report not found' }),
      })

      await expect(getReport('test-id')).rejects.toThrow('Report not found')
    })
  })

  describe('downloadPlaybook', () => {
    it('should download a playbook', async () => {
      const mockPlaybook = '---\n- name: Test Playbook\n  hosts: all'

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: async () => mockPlaybook,
      })

      const result = await downloadPlaybook('session-id')

      expect(result).toBe(mockPlaybook)
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/sessions/session-id/playbook')
    })

    it('should handle download errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Playbook not found' }),
      })

      await expect(downloadPlaybook('session-id')).rejects.toThrow('Playbook not found')
    })
  })
})
