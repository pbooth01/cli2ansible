'use client'

import { AlertCircle, CheckCircle, Loader } from 'lucide-react'

export const LoadingSpinner: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <Loader className="w-8 h-8 text-blue-600 animate-spin" />
      <p className="text-gray-600">{message}</p>
    </div>
  )
}

interface AlertProps {
  variant: 'error' | 'success' | 'info'
  message: string
  title?: string
}

export const Alert: React.FC<AlertProps> = ({ variant, message, title }) => {
  const variantClasses = {
    error: 'bg-red-50 border-red-200 text-red-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  }

  const iconClasses = {
    error: 'text-red-600',
    success: 'text-green-600',
    info: 'text-blue-600',
  }

  const icons = {
    error: <AlertCircle className={`w-5 h-5 ${iconClasses.error}`} />,
    success: <CheckCircle className={`w-5 h-5 ${iconClasses.success}`} />,
    info: <AlertCircle className={`w-5 h-5 ${iconClasses.info}`} />,
  }

  return (
    <div className={`p-4 border rounded-lg ${variantClasses[variant]} flex gap-3`}>
      {icons[variant]}
      <div>
        {title && <h3 className="font-semibold">{title}</h3>}
        <p className={title ? 'text-sm mt-1' : ''}>{message}</p>
      </div>
    </div>
  )
}

interface ProgressProps {
  value: number
  max?: number
  label?: string
  showPercent?: boolean
}

export const Progress: React.FC<ProgressProps> = ({ value, max = 100, label, showPercent = true }) => {
  const percentage = (value / max) * 100

  return (
    <div>
      {(label || showPercent) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          {showPercent && <span className="text-sm text-gray-600">{Math.round(percentage)}%</span>}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

interface BadgeProps {
  label: string
  variant?: 'default' | 'success' | 'warning' | 'error'
}

export const Badge: React.FC<BadgeProps> = ({ label, variant = 'default' }) => {
  const variantClasses = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
  }

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${variantClasses[variant]}`}>
      {label}
    </span>
  )
}

interface ToastProps {
  variant: 'success' | 'error' | 'info'
  message: string
  isVisible: boolean
}

export const Toast: React.FC<ToastProps> = ({ variant, message, isVisible }) => {
  if (!isVisible) return null

  const variantClasses = {
    error: 'bg-red-600 text-white',
    success: 'bg-green-600 text-white',
    info: 'bg-blue-600 text-white',
  }

  const iconClasses = {
    error: 'text-red-200',
    success: 'text-green-200',
    info: 'text-blue-200',
  }

  const icons = {
    error: <AlertCircle className={`w-5 h-5 ${iconClasses.error}`} />,
    success: <CheckCircle className={`w-5 h-5 ${iconClasses.success}`} />,
    info: <AlertCircle className={`w-5 h-5 ${iconClasses.info}`} />,
  }

  return (
    <div className={`fixed top-4 right-4 ${variantClasses[variant]} px-6 py-4 rounded-lg shadow-lg flex gap-3 items-start max-w-md animate-in slide-in-from-right z-50`}>
      {icons[variant]}
      <p className="flex-1 text-sm">{message}</p>
    </div>
  )
}
