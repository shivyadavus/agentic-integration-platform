'use client'

import { motion } from 'framer-motion'
import { 
  Activity, 
  Zap, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  Clock
} from 'lucide-react'

interface Integration {
  id: string
  name: string
  status: string
  integration_type: string
  created_at: string
  processing_time_seconds?: number
}

interface MetricsCardsProps {
  integrations: Integration[]
  statusCounts: Record<string, number>
}

export function MetricsCards({ integrations, statusCounts }: MetricsCardsProps) {
  const totalIntegrations = integrations.length
  const activeIntegrations = statusCounts.active || 0
  const errorIntegrations = statusCounts.error || 0
  const avgProcessingTime = integrations
    .filter(i => i.processing_time_seconds)
    .reduce((acc, i) => acc + (i.processing_time_seconds || 0), 0) / 
    integrations.filter(i => i.processing_time_seconds).length || 0

  const metrics = [
    {
      title: 'Total Integrations',
      value: totalIntegrations,
      change: '+12%',
      changeType: 'positive' as const,
      icon: Activity,
      color: 'blue',
      description: 'All time integrations'
    },
    {
      title: 'Active Integrations',
      value: activeIntegrations,
      change: '+8%',
      changeType: 'positive' as const,
      icon: CheckCircle,
      color: 'green',
      description: 'Currently running'
    },
    {
      title: 'Success Rate',
      value: totalIntegrations > 0 ? Math.round(((totalIntegrations - errorIntegrations) / totalIntegrations) * 100) : 0,
      suffix: '%',
      change: '+2.1%',
      changeType: 'positive' as const,
      icon: TrendingUp,
      color: 'emerald',
      description: 'Integration success'
    },
    {
      title: 'Avg Processing',
      value: Math.round(avgProcessingTime) || 0,
      suffix: 's',
      change: '-0.5s',
      changeType: 'positive' as const,
      icon: Clock,
      color: 'purple',
      description: 'Processing time'
    }
  ]

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'blue':
        return {
          bg: 'bg-blue-500',
          light: 'bg-blue-100 dark:bg-blue-900/20',
          text: 'text-blue-600 dark:text-blue-400'
        }
      case 'green':
        return {
          bg: 'bg-green-500',
          light: 'bg-green-100 dark:bg-green-900/20',
          text: 'text-green-600 dark:text-green-400'
        }
      case 'emerald':
        return {
          bg: 'bg-emerald-500',
          light: 'bg-emerald-100 dark:bg-emerald-900/20',
          text: 'text-emerald-600 dark:text-emerald-400'
        }
      case 'purple':
        return {
          bg: 'bg-purple-500',
          light: 'bg-purple-100 dark:bg-purple-900/20',
          text: 'text-purple-600 dark:text-purple-400'
        }
      default:
        return {
          bg: 'bg-gray-500',
          light: 'bg-gray-100 dark:bg-gray-900/20',
          text: 'text-gray-600 dark:text-gray-400'
        }
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metrics.map((metric, index) => {
        const colors = getColorClasses(metric.color)
        const Icon = metric.icon
        
        return (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg ${colors.light}`}>
                <Icon className={`h-5 w-5 ${colors.text}`} />
              </div>
              
              <div className={`text-xs px-2 py-1 rounded-full ${
                metric.changeType === 'positive' 
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                  : 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
              }`}>
                {metric.change}
              </div>
            </div>
            
            <div className="space-y-1">
              <div className="flex items-baseline space-x-1">
                <span className="text-2xl font-bold text-slate-900 dark:text-white">
                  {metric.value}
                </span>
                {metric.suffix && (
                  <span className="text-sm text-slate-500 dark:text-slate-400">
                    {metric.suffix}
                  </span>
                )}
              </div>
              
              <h3 className="font-medium text-slate-900 dark:text-white">
                {metric.title}
              </h3>
              
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {metric.description}
              </p>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
