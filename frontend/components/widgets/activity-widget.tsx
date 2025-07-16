'use client'

import { motion } from 'framer-motion'
import { formatDistanceToNow } from 'date-fns'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Activity, GitBranch, CheckCircle, AlertCircle, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ActivityItem {
  id: string
  type: 'integration_created' | 'integration_deployed' | 'integration_failed' | 'system_update'
  title: string
  description: string
  timestamp: Date
  user?: {
    name: string
    avatar?: string
    initials: string
  }
  status?: 'success' | 'warning' | 'error' | 'info'
}

interface ActivityWidgetProps {
  activities?: ActivityItem[]
  className?: string
}

const defaultActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'integration_created',
    title: 'New Slack Integration',
    description: 'Created Slack to Notion workflow integration',
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    user: { name: 'Sarah Chen', initials: 'SC' },
    status: 'success'
  },
  {
    id: '2',
    type: 'integration_deployed',
    title: 'Salesforce Integration Live',
    description: 'Successfully deployed CRM sync integration',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    user: { name: 'Mike Johnson', initials: 'MJ' },
    status: 'success'
  },
  {
    id: '3',
    type: 'integration_failed',
    title: 'API Rate Limit Exceeded',
    description: 'GitHub integration temporarily paused',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    status: 'error'
  },
  {
    id: '4',
    type: 'system_update',
    title: 'System Maintenance',
    description: 'Scheduled maintenance completed successfully',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    status: 'info'
  }
]

const getActivityIcon = (type: ActivityItem['type']) => {
  switch (type) {
    case 'integration_created':
      return <GitBranch className="h-4 w-4" />
    case 'integration_deployed':
      return <CheckCircle className="h-4 w-4" />
    case 'integration_failed':
      return <AlertCircle className="h-4 w-4" />
    case 'system_update':
      return <Activity className="h-4 w-4" />
    default:
      return <Clock className="h-4 w-4" />
  }
}

const getStatusColor = (status: ActivityItem['status']) => {
  switch (status) {
    case 'success':
      return 'text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/30'
    case 'error':
      return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30'
    case 'warning':
      return 'text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/30'
    case 'info':
      return 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30'
    default:
      return 'text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-900/30'
  }
}

export function ActivityWidget({ activities = defaultActivities, className }: ActivityWidgetProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className={className}
    >
      <Card className="h-full bg-gradient-to-br from-white/90 to-slate-50/90 dark:from-slate-900/90 dark:to-slate-800/90 backdrop-blur-sm border border-slate-200/30 dark:border-slate-700/30 shadow-xl">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center space-x-2">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <span>Recent Activity</span>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
          {activities.map((activity, index) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="flex items-start space-x-3 p-3 rounded-xl hover:bg-slate-100/50 dark:hover:bg-slate-800/50 transition-colors group"
            >
              <div className="flex-shrink-0">
                {activity.user ? (
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={activity.user.avatar} />
                    <AvatarFallback className="bg-gradient-to-br from-purple-500 to-blue-500 text-white text-sm font-semibold">
                      {activity.user.initials}
                    </AvatarFallback>
                  </Avatar>
                ) : (
                  <div className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center',
                    getStatusColor(activity.status)
                  )}>
                    {getActivityIcon(activity.type)}
                  </div>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-slate-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                    {activity.title}
                  </p>
                  {activity.status && (
                    <Badge variant="secondary" className={cn(
                      'text-xs',
                      getStatusColor(activity.status)
                    )}>
                      {activity.status}
                    </Badge>
                  )}
                </div>
                
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                  {activity.description}
                </p>
                
                <div className="flex items-center space-x-2 mt-2">
                  <Clock className="h-3 w-3 text-slate-400" />
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                  </span>
                  {activity.user && (
                    <>
                      <span className="text-xs text-slate-400">•</span>
                      <span className="text-xs text-slate-500 dark:text-slate-400">
                        by {activity.user.name}
                      </span>
                    </>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </CardContent>
      </Card>
    </motion.div>
  )
}