'use client'

import { motion } from 'framer-motion'
import { 
  Plus, 
  Zap, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Settings,
  Play
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

interface Integration {
  id: string
  name: string
  status: string
  created_at: string
  updated_at: string
}

interface ActivityFeedProps {
  integrations: Integration[]
}

export function ActivityFeed({ integrations }: ActivityFeedProps) {
  // Generate activity items from integrations
  const activities = integrations
    .slice(0, 10) // Show last 10 activities
    .map(integration => ({
      id: integration.id,
      type: getActivityType(integration.status),
      title: getActivityTitle(integration.status, integration.name),
      description: getActivityDescription(integration.status),
      timestamp: integration.updated_at,
      icon: getActivityIcon(integration.status),
      color: getActivityColor(integration.status)
    }))
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

  function getActivityType(status: string) {
    switch (status.toLowerCase()) {
      case 'draft':
        return 'created'
      case 'generating':
        return 'processing'
      case 'active':
        return 'deployed'
      case 'error':
        return 'error'
      default:
        return 'updated'
    }
  }

  function getActivityTitle(status: string, name: string) {
    switch (status.toLowerCase()) {
      case 'draft':
        return `Integration "${name}" created`
      case 'generating':
        return `Processing "${name}"`
      case 'active':
        return `Integration "${name}" deployed`
      case 'error':
        return `Error in "${name}"`
      default:
        return `Integration "${name}" updated`
    }
  }

  function getActivityDescription(status: string) {
    switch (status.toLowerCase()) {
      case 'draft':
        return 'New integration created and ready for configuration'
      case 'generating':
        return 'AI is generating integration code and configuration'
      case 'active':
        return 'Integration is now live and processing requests'
      case 'error':
        return 'Integration encountered an error and needs attention'
      default:
        return 'Integration status updated'
    }
  }

  function getActivityIcon(status: string) {
    switch (status.toLowerCase()) {
      case 'draft':
        return Plus
      case 'generating':
        return Zap
      case 'active':
        return CheckCircle
      case 'error':
        return AlertCircle
      default:
        return Settings
    }
  }

  function getActivityColor(status: string) {
    switch (status.toLowerCase()) {
      case 'draft':
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20'
      case 'generating':
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20'
      case 'active':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20'
      case 'error':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20'
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20'
    }
  }

  if (activities.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6">
        <div className="text-center py-8">
          <Clock className="h-12 w-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
            No recent activity
          </h3>
          <p className="text-slate-500 dark:text-slate-400">
            Activity will appear here as you create and manage integrations
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6">
      <div className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = activity.icon
          
          return (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-start space-x-3 pb-4 last:pb-0 border-b border-slate-100 dark:border-slate-700 last:border-0"
            >
              <div className={`p-2 rounded-full ${activity.color}`}>
                <Icon className="h-4 w-4" />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 dark:text-white">
                  {activity.title}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {activity.description}
                </p>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-2">
                  {formatDate(activity.timestamp)}
                </p>
              </div>
            </motion.div>
          )
        })}
      </div>
      
      <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
        <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium">
          View all activity →
        </button>
      </div>
    </div>
  )
}
