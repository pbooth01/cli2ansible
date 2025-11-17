'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Upload } from 'lucide-react'
import { createSession, uploadCastFile } from '@/lib/api'
import { Button } from '@/components/Button'
import { Input, TextArea } from '@/components/Input'
import { Card, CardHeader, CardBody, CardFooter } from '@/components/Card'
import { Alert, LoadingSpinner } from '@/components/Status'

type Step = 'details' | 'upload'

export default function CreatePage() {
  const router = useRouter()

  const [step, setStep] = useState<Step>('details')
  const [formData, setFormData] = useState({
    name: '',
    metadata: '',
  })
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [createError, setCreateError] = useState<string | null>(null)
  const [uploadLoading, setUploadLoading] = useState(false)
  const [createLoading, setCreateLoading] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.name.trim()) {
      return
    }

    setCreateLoading(true)
    setCreateError(null)

    try {
      let metadata = {}
      if (formData.metadata.trim()) {
        metadata = JSON.parse(formData.metadata)
      }

      const session = await createSession(formData.name, metadata)
      setSessionId(session.id)
      setStep('upload')
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : 'Failed to create session')
    } finally {
      setCreateLoading(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !sessionId) return

    setUploadError(null)
    setUploadLoading(true)

    try {
      if (!file.name.endsWith('.cast')) {
        throw new Error('Please upload a .cast file (asciinema format)')
      }

      await uploadCastFile(sessionId, file)
      router.push(`/sessions/${sessionId}`)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Failed to upload file')
    } finally {
      setUploadLoading(false)
    }
  }

  const handleSkipUpload = () => {
    if (sessionId) {
      router.push(`/sessions/${sessionId}`)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      {step === 'details' ? (
        <Card>
          <CardHeader title="Create New Session" subtitle="Start by naming your terminal session" />

          <form onSubmit={handleCreateSession}>
            <CardBody className="space-y-6">
              {createError && (
                <Alert variant="error" title="Error" message={createError} />
              )}

              <Input
                label="Session Name"
                name="name"
                placeholder="e.g., Ubuntu Server Setup, Database Migration"
                value={formData.name}
                onChange={handleInputChange}
                helper="A descriptive name for your terminal session"
              />

              <TextArea
                label="Metadata (optional)"
                name="metadata"
                placeholder={'{\n  "environment": "production",\n  "target_os": "ubuntu-22.04"\n}'}
                rows={6}
                value={formData.metadata}
                onChange={handleInputChange}
                helper="Optional JSON metadata to describe this session"
              />
            </CardBody>

            <CardFooter>
              <Button type="submit" loading={createLoading}>
                Next
              </Button>
            </CardFooter>
          </form>
        </Card>
      ) : (
        <Card>
          <CardHeader title="Upload Session" subtitle="Upload a .cast file or skip for manual entry" />

          {uploadLoading ? (
            <CardBody>
              <LoadingSpinner message="Uploading session..." />
            </CardBody>
          ) : (
            <CardBody className="space-y-6">
              {uploadError && (
                <Alert variant="error" title="Upload Error" message={uploadError} />
              )}

              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 hover:bg-blue-50 transition-colors">
                <input
                  type="file"
                  accept=".cast"
                  onChange={handleFileUpload}
                  disabled={uploadLoading}
                  className="hidden"
                  id="cast-file"
                />
                <label htmlFor="cast-file" className="cursor-pointer flex flex-col items-center gap-3">
                  <Upload className="w-12 h-12 text-gray-400" />
                  <div>
                    <p className="font-semibold text-gray-900">Click to upload .cast file</p>
                    <p className="text-sm text-gray-600">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">
                    .cast files from asciinema. Maximum 10MB
                  </p>
                </label>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">or</span>
                </div>
              </div>

              <p className="text-center text-sm text-gray-600">
                You can add events manually after creating the session
              </p>
            </CardBody>
          )}

          {!uploadLoading && (
            <CardFooter className="justify-between">
              <Button
                variant="secondary"
                onClick={() => setStep('details')}
                disabled={uploadLoading}
              >
                Back
              </Button>
              <Button
                variant="secondary"
                onClick={handleSkipUpload}
                disabled={uploadLoading}
              >
                Skip Upload
              </Button>
            </CardFooter>
          )}
        </Card>
      )}
    </div>
  )
}
