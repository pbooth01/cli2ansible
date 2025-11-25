'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Download, Zap, BarChart3, Upload, Trash2 } from 'lucide-react'
import { getSession, compileSession, getReport, downloadPlaybook, uploadCastFile, deleteSession, Session, Report } from '@/lib/api'
import { Button } from '@/components/Button'
import { Card, CardHeader, CardBody, CardFooter } from '@/components/Card'
import { LoadingSpinner, Alert, Badge, Progress, Toast } from '@/components/Status'

type Tab = 'overview' | 'report'

export default function SessionDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params?.id as string
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [session, setSession] = useState<Session | null>(null)
  const [report, setReport] = useState<Report | null>(null)
  const [sessionLoading, setSessionLoading] = useState(true)
  const [reportLoading, setReportLoading] = useState(false)
  const [compileLoading, setCompileLoading] = useState(false)
  const [downloadLoading, setDownloadLoading] = useState(false)
  const [uploadLoading, setUploadLoading] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [compileError, setCompileError] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [activeTab, setActiveTab] = useState<Tab>('overview')
  const [toastMessage, setToastMessage] = useState<string | null>(null)
  const [toastVariant, setToastVariant] = useState<'success' | 'error' | 'info'>('success')
  const [showToast, setShowToast] = useState(false)
  const toastTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!sessionId) return

    const fetchSession = async () => {
      try {
        setSessionLoading(true)
        const data = await getSession(sessionId)
        setSession(data)
      } catch (err) {
        console.error('Failed to load session:', err)
      } finally {
        setSessionLoading(false)
      }
    }

    fetchSession()
  }, [sessionId])

  // Cleanup toast timeout on unmount
  useEffect(() => {
    return () => {
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current)
      }
    }
  }, [])

  const handleCompile = async () => {
    if (!sessionId) return

    try {
      setCompileLoading(true)
      setCompileError(null)
      await compileSession(sessionId)

      const updatedSession = await getSession(sessionId)
      setSession(updatedSession)

      const reportData = await getReport(sessionId)
      setReport(reportData)
      setActiveTab('report')
    } catch (err) {
      setCompileError(err instanceof Error ? err.message : 'Failed to compile session')
    } finally {
      setCompileLoading(false)
    }
  }

  const handleFetchReport = async () => {
    if (!sessionId) return

    try {
      setReportLoading(true)
      const reportData = await getReport(sessionId)
      setReport(reportData)
      setActiveTab('report')
    } catch (err) {
      console.error('Failed to fetch report:', err)
    } finally {
      setReportLoading(false)
    }
  }

  const handleDownload = async () => {
    if (!sessionId) return

    try {
      setDownloadLoading(true)
      const data = await downloadPlaybook(sessionId)

      const url = window.URL.createObjectURL(new Blob([data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `role_${sessionId}.zip`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download failed:', err)
    } finally {
      setDownloadLoading(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !sessionId) return

    setUploadError(null)
    setUploadSuccess(null)
    setUploadLoading(true)

    try {
      if (!file.name.endsWith('.cast')) {
        throw new Error('Please upload a .cast file (asciinema format)')
      }

      await uploadCastFile(sessionId, file)
      setUploadSuccess('Cast file uploaded successfully! Compiling session...')

      // Show toast with filename
      setToastVariant('success')
      setToastMessage(`Uploaded "${file.name}" (${(file.size / 1024).toFixed(2)} KB)`)
      setShowToast(true)

      // Auto-dismiss toast after 4 seconds
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current)
      }
      toastTimeoutRef.current = setTimeout(() => {
        setShowToast(false)
      }, 4000)

      // Refresh session data (this will show the cast file and new compilation status)
      const updatedSession = await getSession(sessionId)
      setSession(updatedSession)

      // Fetch report to ensure compilation is complete
      try {
        const reportData = await getReport(sessionId)
        setReport(reportData)
      } catch (err) {
        console.error('Failed to fetch report:', err)
      }

      // Clear success message now that compilation is done
      setUploadSuccess(null)

      // Auto-switch to report tab after compilation
      setActiveTab('report')

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload file'
      setUploadError(errorMessage)

      // Show error toast
      setToastVariant('error')
      setToastMessage(errorMessage)
      setShowToast(true)

      // Auto-dismiss error toast after 5 seconds
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current)
      }
      toastTimeoutRef.current = setTimeout(() => {
        setShowToast(false)
      }, 5000)
    } finally {
      setUploadLoading(false)
    }
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  const handleDelete = async () => {
    if (!sessionId) return

    try {
      setDeleteLoading(true)
      setDeleteError(null)
      await deleteSession(sessionId)
      // Delay slightly before redirect to allow UI to update
      setTimeout(() => {
        router.push('/sessions')
      }, 500)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to delete session'
      console.error('Failed to delete session:', err)
      setDeleteError(errorMsg)
      setDeleteLoading(false)
    }
  }

  if (!sessionId) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-8">
        <Alert variant="error" title="Error" message="Session ID is required" />
      </div>
    )
  }

  if (sessionLoading) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-8">
        <LoadingSpinner message="Loading session..." />
      </div>
    )
  }

  if (!session) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-8">
        <Alert variant="error" title="Not Found" message="Session not found" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
      {/* Toast Notification */}
      <Toast variant={toastVariant} message={toastMessage || ''} isVisible={showToast} />

      {/* Confirmation Dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader title="Delete Session" subtitle="This action cannot be undone" />
            <CardBody className="space-y-4">
              {deleteError && (
                <Alert variant="error" title="Error" message={deleteError} />
              )}
              <p className="text-gray-700">
                Are you sure you want to delete the session <span className="font-semibold">{session?.name}</span>? All associated events, commands, and generated files will be permanently deleted.
              </p>
            </CardBody>
            <CardFooter className="justify-end gap-2">
              <Button
                variant="secondary"
                onClick={() => {
                  setShowDeleteConfirm(false)
                  setDeleteError(null)
                }}
                disabled={deleteLoading}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleDelete}
                loading={deleteLoading}
                className="flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {/* Header Card */}
      <Card>
        <CardHeader
          title={session.name}
          subtitle={`Created on ${new Date(session.created_at).toLocaleDateString()}`}
        />
        <CardBody className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Session ID</p>
              <p className="font-mono text-sm text-gray-900 truncate">{session.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <Badge
                label={session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                variant={
                  session.status === 'completed'
                    ? 'success'
                    : session.status === 'failed'
                      ? 'error'
                      : 'warning'
                }
              />
            </div>
            <div>
              <p className="text-sm text-gray-600">Created</p>
              <p className="text-sm text-gray-900">
                {new Date(session.created_at).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Last Updated</p>
              <p className="text-sm text-gray-900">
                {new Date(session.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </CardBody>
        <CardFooter className="justify-end">
          <Button
            variant="danger"
            onClick={() => setShowDeleteConfirm(true)}
            disabled={deleteLoading}
            className="flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Delete Session
          </Button>
        </CardFooter>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'overview'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Overview
        </button>
        <button
          onClick={handleFetchReport}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'report'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Report
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' ? (
        <>
          {/* File Upload Card */}
          <Card>
            <CardHeader title="Upload Cast File" subtitle="Add a terminal session recording to this session" />

            {uploadError && (
              <CardBody className="mb-4">
                <Alert variant="error" title="Upload Error" message={uploadError} />
              </CardBody>
            )}

            {uploadSuccess && (
              <CardBody className="mb-4">
                <Alert variant="info" title="Success" message={uploadSuccess} />
              </CardBody>
            )}

            <CardBody className="space-y-4">
              {session?.cast_file && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-gray-600">Current cast file:</p>
                  <p className="text-sm font-medium text-gray-900">{session.cast_file.file_name}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {(session.cast_file.file_size / 1024).toFixed(2)} KB • Uploaded {new Date(session.cast_file.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
              )}
              <p className="text-gray-600">
                {session?.cast_file ? 'Upload a new file to replace the current one.' : 'Upload an asciinema .cast file to populate this session with terminal events.'}
              </p>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
                   onClick={triggerFileInput}>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".cast"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploadLoading}
                />
                <p className="text-gray-700 font-medium">Drag and drop your .cast file here</p>
                <p className="text-gray-500 text-sm mt-2">or click to browse</p>
              </div>
            </CardBody>

            <CardFooter>
              <Button
                onClick={triggerFileInput}
                loading={uploadLoading}
                className="flex items-center gap-2"
              >
                <Upload className="w-4 h-4" />
                Choose File
              </Button>
            </CardFooter>
          </Card>

          {/* Compilation Card */}
          <Card>
            <CardHeader title="Compilation" subtitle="Convert this session to an Ansible playbook" />

            {compileError && (
              <CardBody className="mb-4">
                <Alert variant="error" title="Compilation Error" message={compileError} />
              </CardBody>
            )}

            <CardBody className="space-y-4">
            <p className="text-gray-600">
              {session?.cast_file
                ? 'Your session was automatically compiled after the cast file upload. Check the Report tab to see the results.'
                : 'Upload a cast file and your terminal session will be automatically compiled into a production-ready Ansible role.'}
            </p>
            {!session?.cast_file && (
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1">✓</span>
                  <span>Extracts commands from the session</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1">✓</span>
                  <span>Translates shell commands to Ansible modules</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1">✓</span>
                  <span>Generates a complete Ansible role with tests</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1">✓</span>
                  <span>Provides confidence scores for each translation</span>
                </li>
              </ul>
            )}
          </CardBody>

          <CardFooter className="justify-between">
            <div className="text-sm text-gray-600">
              {session.status === 'completed'
                ? '✓ This session has been compiled'
                : 'Upload a cast file to automatically compile'}
            </div>
            <div className="flex gap-2">
              {!session?.cast_file && (
                <Button
                  onClick={handleCompile}
                  loading={compileLoading}
                  className="flex items-center gap-2"
                >
                  <Zap className="w-4 h-4" />
                  Compile Session
                </Button>
              )}
              {session.status === 'completed' && (
                <Button
                  onClick={handleDownload}
                  loading={downloadLoading}
                  variant="secondary"
                  className="flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download Role
                </Button>
              )}
            </div>
          </CardFooter>
          </Card>
        </>
      ) : (
        <Card>
          <CardHeader title="Compilation Report" subtitle="Detailed analysis of the translation" />

          {reportLoading ? (
            <CardBody>
              <LoadingSpinner message="Loading report..." />
            </CardBody>
          ) : report ? (
            <>
            <CardBody className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4">Command Summary</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-600">Total Commands</p>
                      <p className="text-2xl font-bold text-gray-900">{report.total_commands}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-2">Confidence Distribution</p>
                      <div className="space-y-2">
                        <Progress
                          value={report.high_confidence}
                          max={report.total_commands}
                          label={`High (${report.high_confidence})`}
                          showPercent={false}
                        />
                        <Progress
                          value={report.medium_confidence}
                          max={report.total_commands}
                          label={`Medium (${report.medium_confidence})`}
                          showPercent={false}
                        />
                        <Progress
                          value={report.low_confidence}
                          max={report.total_commands}
                          label={`Low (${report.low_confidence})`}
                          showPercent={false}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-4">Statistics</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Session Duration</span>
                      <span className="font-medium text-gray-900">
                        {Math.round(report.session_duration_seconds)}s
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Sudo Commands</span>
                      <span className="font-medium text-gray-900">{report.sudo_command_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Skipped Commands</span>
                      <span className="font-medium text-gray-900">{report.skipped_commands}</span>
                    </div>
                  </div>
                </div>
              </div>

              {report.module_breakdown && Object.keys(report.module_breakdown).length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Module Breakdown</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {Object.entries(report.module_breakdown).map(([module, count]) => (
                      <Badge
                        key={module}
                        label={`${module} (${count})`}
                        variant="default"
                      />
                    ))}
                  </div>
                </div>
              )}

              {report.warnings && report.warnings.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Warnings</h3>
                  <div className="space-y-2">
                    {report.warnings.map((warning, idx) => (
                      <Alert key={idx} variant="info" message={warning} />
                    ))}
                  </div>
                </div>
              )}

              {report.most_common_commands && report.most_common_commands.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Most Common Commands</h3>
                  <div className="space-y-2">
                    {report.most_common_commands.slice(0, 5).map((cmd, idx) => (
                      <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="font-mono text-sm text-gray-700">{cmd.command}</span>
                        <Badge label={`${cmd.count}x`} variant="default" />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardBody>
            {session?.status === 'completed' && (
              <CardFooter className="justify-end gap-2">
                <Button
                  onClick={handleDownload}
                  loading={downloadLoading}
                  variant="secondary"
                  className="flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download Role
                </Button>
              </CardFooter>
            )}
            </>
          ) : (
            <CardBody className="text-center py-12">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 mb-4">No report available yet</p>
              <Button onClick={handleCompile} loading={compileLoading}>
                Compile to Generate Report
              </Button>
            </CardBody>
          )}
        </Card>
      )}
    </div>
  )
}
