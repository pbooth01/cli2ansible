import Link from 'next/link'
import { FileText, Upload, Zap } from 'lucide-react'
import { Button } from '@/components/Button'
import { Card, CardBody, CardHeader } from '@/components/Card'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-6 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl mx-auto mb-6">
            <span className="text-white font-bold text-4xl">c2a</span>
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Convert Terminal Sessions to Ansible
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Record your terminal commands and automatically generate reproducible Ansible playbooks and roles.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href="/create">
              <Button size="lg">Create New Session</Button>
            </Link>
            <Link href="/sessions">
              <Button size="lg" variant="secondary">
                View Sessions
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card className="text-center">
            <CardBody>
              <Upload className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Sessions</h3>
              <p className="text-gray-600">
                Upload .cast files from asciinema or manually create sessions and add events.
              </p>
            </CardBody>
          </Card>

          <Card className="text-center">
            <CardBody>
              <Zap className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Translation</h3>
              <p className="text-gray-600">
                Intelligently translates shell commands to Ansible modules with confidence scoring.
              </p>
            </CardBody>
          </Card>

          <Card className="text-center">
            <CardBody>
              <FileText className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Generate Playbooks</h3>
              <p className="text-gray-600">
                Creates production-ready Ansible roles with tests, documentation, and best practices.
              </p>
            </CardBody>
          </Card>
        </div>

        {/* Getting Started Section */}
        <Card>
          <CardHeader title="Getting Started" subtitle="Follow these steps to convert your first session" />
          <CardBody className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white font-bold">
                  1
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Create a Session</h4>
                <p className="text-gray-600">Start by creating a new session with a descriptive name.</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white font-bold">
                  2
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Upload Terminal Recording</h4>
                <p className="text-gray-600">
                  Upload a .cast file from asciinema or input your terminal commands manually.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white font-bold">
                  3
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Review & Compile</h4>
                <p className="text-gray-600">
                  Review the extracted commands and compile them into an Ansible playbook.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white font-bold">
                  4
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Download & Use</h4>
                <p className="text-gray-600">
                  Download the generated role and integrate it into your Ansible projects.
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
