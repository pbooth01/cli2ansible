/**
 * Tests for API client
 */

import {
  createSession,
  listSessions,
  getSession,
  deleteSession,
  uploadCastFile,
  compileSession,
  getReport,
  downloadPlaybook,
} from '../api'

// Mock fetch globally
global.fetch = jest.fn()

describe('API Client', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks()
  })

  describe('createSession', () => {
    it('should create a session successfully', async () => {
      const mockSession = {
        id: 'session-123',
        name: 'Test Session',
        status: 'created',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        metadata: {},
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await createSession('Test Session', {})

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: 'Test Session', metadata: {} }),
      })
      expect(result).toEqual(mockSession)
    })

    it('should handle creation errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Session name already exists' }),
      })

      await expect(createSession('Duplicate')).rejects.toThrow(
        'Session name already exists'
      )
    })

    it('should handle network errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => {
          throw new Error('Network error')
        },
      })

      await expect(createSession('Test')).rejects.toThrow(
        'Failed to create session'
      )
    })
  })

  describe('listSessions', () => {
    it('should list all sessions', async () => {
      const mockSessions = [
        {
          id: 'session-1',
          name: 'Session 1',
          status: 'created',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          metadata: {},
        },
        {
          id: 'session-2',
          name: 'Session 2',
          status: 'compiled',
          created_at: '2024-01-02T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
          metadata: {},
        },
      ]

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ sessions: mockSessions }),
      })

      const result = await listSessions()

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/sessions')
      expect(result).toEqual(mockSessions)
    })

    it('should return empty array when no sessions key', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      })

      const result = await listSessions()
      expect(result).toEqual([])
    })

    it('should handle fetch errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
      })

      await expect(listSessions()).rejects.toThrow('Failed to fetch sessions')
    })
  })

  describe('getSession', () => {
    it('should get a session by ID', async () => {
      const mockSession = {
        id: 'session-123',
        name: 'Test Session',
        status: 'created',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        metadata: {},
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSession,
      })

      const result = await getSession('session-123')

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/sessions/session-123')
      expect(result).toEqual(mockSession)
    })

    it('should handle session not found', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Session not found' }),
      })

      await expect(getSession('invalid-id')).rejects.toThrow(
        'Session not found'
      )
    })

    it('should handle network errors gracefully', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => {
          throw new Error('Network error')
        },
      })

      await expect(getSession('session-123')).rejects.toThrow(
        'Session not found'
      )
    })
  })

  describe('deleteSession', () => {
    it('should delete a session successfully', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
      })

      await deleteSession('session-123')

      expect(global.fetch).toHaveBeenCalledWith('/api/v1/sessions/session-123', {
        method: 'DELETE',
      })
    })

    it('should handle deletion errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Session not found' }),
      })

      await expect(deleteSession('invalid-id')).rejects.toThrow(
        'Session not found'
      )
    })

    it('should handle network errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => {
          throw new Error('Network error')
        },
      })

      await expect(deleteSession('session-123')).rejects.toThrow(
        'Failed to delete session'
      )
    })
  })

  describe('uploadCastFile', () => {
    it('should upload a cast file successfully', async () => {
      const mockFile = new File(['content'], 'test.cast', {
        type: 'application/json',
      })

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
      })

      await uploadCastFile('session-123', mockFile)

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/sessions/session-123/cast',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        })
      )
    })

    it('should handle upload errors', async () => {
      const mockFile = new File(['content'], 'test.cast', {
        type: 'application/json',
      })

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid file format' }),
      })

      await expect(uploadCastFile('session-123', mockFile)).rejects.toThrow(
        'Invalid file format'
      )
    })

    it('should handle network errors', async () => {
      const mockFile = new File(['content'], 'test.cast', {
        type: 'application/json',
      })

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => {
          throw new Error('Network error')
        },
      })

      await expect(uploadCastFile('session-123', mockFile)).rejects.toThrow(
        'Failed to upload file'
      )
    })
  })

  describe('compileSession', () => {
    it('should compile a session successfully', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
      })

      await compileSession('session-123')

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/sessions/session-123/compile',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({}),
        }
      )
    })

    it('should handle compilation errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'No cast file uploaded' }),
      })

      await expect(compileSession('session-123')).rejects.toThrow(
        'No cast file uploaded'
      )
    })

    it('should handle network errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => {
          throw new Error('Network error')
        },
      })

      await expect(compileSession('session-123')).rejects.toThrow(
        'Failed to compile session'
      )
    })
  })

  describe('getReport', () => {
    it('should get a compilation report', async () => {
      const mockReport = {
        session_id: 'session-123',
        total_commands: 10,
        high_confidence: 8,
        medium_confidence: 2,
        low_confidence: 0,
        skipped_commands: 0,
        sudo_command_count: 3,
        session_duration_seconds: 120,
        module_breakdown: { shell: 5, apt: 3, copy: 2 },
        most_common_commands: [
          { command: 'ls', count: 3 },
          { command: 'cd', count: 2 },
        ],
        warnings: [],
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockReport,
      })

      const result = await getReport('session-123')

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/sessions/session-123/report'
      )
      expect(result).toEqual(mockReport)
    })

    it('should handle report not found', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Report not found' }),
      })

      await expect(getReport('session-123')).rejects.toThrow(
        'Report not found'
      )
    })

    it('should handle network errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => {
          throw new Error('Network error')
        },
      })

      await expect(getReport('session-123')).rejects.toThrow(
        'Failed to fetch report'
      )
    })
  })

  describe('downloadPlaybook', () => {
    it('should download a playbook successfully', async () => {
      const mockPlaybook = '---\n- name: Test Playbook\n  hosts: all\n  tasks: []'

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        text: async () => mockPlaybook,
      })

      const result = await downloadPlaybook('session-123')

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/sessions/session-123/playbook'
      )
      expect(result).toEqual(mockPlaybook)
    })

    it('should handle playbook not found', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Playbook not found' }),
      })

      await expect(downloadPlaybook('session-123')).rejects.toThrow(
        'Playbook not found'
      )
    })

    it('should handle network errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => {
          throw new Error('Network error')
        },
      })

      await expect(downloadPlaybook('session-123')).rejects.toThrow(
        'Failed to download playbook'
      )
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty session name', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Session name cannot be empty' }),
      })

      await expect(createSession('')).rejects.toThrow(
        'Session name cannot be empty'
      )
    })

    it('should handle special characters in session ID', async () => {
      const sessionId = 'session-with-special-chars-123'
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: sessionId,
          name: 'Test',
          status: 'created',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          metadata: {},
        }),
      })

      const result = await getSession(sessionId)
      expect(result.id).toBe(sessionId)
    })

    it('should handle large metadata objects', async () => {
      const largeMetadata = {
        key1: 'value1'.repeat(100),
        key2: 'value2'.repeat(100),
        nested: {
          deep: {
            data: 'test'.repeat(50),
          },
        },
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 'session-123',
          name: 'Test',
          status: 'created',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          metadata: largeMetadata,
        }),
      })

      const result = await createSession('Test', largeMetadata)
      expect(result.metadata).toEqual(largeMetadata)
    })
  })
})

