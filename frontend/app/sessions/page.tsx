'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Plus, Clock, FileText, Tag } from 'lucide-react'
import { listSessions, Session } from '@/lib/api'
import { Button } from '@/components/Button'
import { Card, CardHeader, CardBody } from '@/components/Card'
import { LoadingSpinner, Alert, Badge } from '@/components/Status'

const getStatusColor = (status: string) => {
  const colors: Record<string, 'default' | 'success' | 'warning' | 'error'> = {
    created: 'default',
    processing: 'warning',
    compiled: 'success',
    ready: 'success',
    failed: 'error',
  }
  return colors[status] || 'default'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await listSessions()
        setSessions(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch sessions')
      } finally {
        setLoading(false)
      }
    }

    fetchSessions()
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <Card>
        <CardHeader
          title="Sessions"
          subtitle="Manage your terminal session recordings and conversions"
          action={
            <Link href="/create">
              <Button size="sm" className="flex items-center gap-2">
                <Plus className="w-4 h-4" />
                New Session
              </Button>
            </Link>
          }
        />

        <CardBody>
          {error && (
            <div className="mb-6">
              <Alert variant="error" title="Error" message={error} />
            </div>
          )}

          {loading ? (
            <LoadingSpinner message="Loading sessions..." />
          ) : sessions.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 mb-4">No sessions yet</p>
              <Link href="/create">
                <Button>Create Your First Session</Button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-4">
              {sessions.map((session) => (
                <Link key={session.id} href={`/sessions/${session.id}`}>
                  <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors cursor-pointer">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1">{session.name}</h3>
                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                          <div className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {formatDate(session.created_at)}
                          </div>
                          <div className="flex items-center gap-2">
                            Status:
                            <Badge
                              label={session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                              variant={getStatusColor(session.status)}
                            />
                          </div>
                        </div>
                        {session.tags && session.tags.length > 0 && (
                          <div className="flex items-center gap-2 flex-wrap">
                            <Tag className="w-3 h-3 text-gray-500" />
                            {session.tags.map((tag) => (
                              <span
                                key={tag}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-600">
                          Updated {formatDate(session.updated_at)}
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  )
}
