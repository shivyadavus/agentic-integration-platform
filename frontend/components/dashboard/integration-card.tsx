'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Clock, 
  Zap, 
  Settings, 
  Play, 
  Pause, 
  MoreHorizontal,
  ExternalLink,
  Brain
} from 'lucide-react'
import { formatDate, getStatusColor } from '@/lib/utils'

interface Integration {
  id: string
  name: string
  status: string
  integration_type: string
  created_at: string
  updated_at: string
  natural_language_spec: string
  ai_model_used?: string
  processing_time_seconds?: number
}

interface IntegrationCardProps {
  integration: Integration
}

export function IntegrationCard({ integration }: IntegrationCardProps) {
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <Play className="h-3 w-3" />
      case 'generating':
        return <Zap className="h-3 w-3 animate-pulse" />
      case 'draft':
        return <Pause className="h-3 w-3" />
      default:
        return <Clock className="h-3 w-3" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'sync':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
      case 'async':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300'
      case 'webhook':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300'
    }
  }

  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="group relative bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6 hover:shadow-2xl hover:shadow-purple-500/10 dark:hover:shadow-purple-500/5 transition-all duration-300 overflow-hidden"
    >
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-transparent to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <div className="relative flex items-start justify-between mb-6">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-3">
            <h3 className="font-bold text-xl bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
              {integration.name}
            </h3>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <Badge className={`${getStatusColor(integration.status)} border-0 px-3 py-1 rounded-full font-semibold shadow-sm`}>
                {getStatusIcon(integration.status)}
                <span className="ml-1 capitalize">{integration.status}</span>
              </Badge>
            </motion.div>
          </div>
          
          <p className="text-slate-600 dark:text-slate-300 text-sm mb-3 line-clamp-2">
            {integration.natural_language_spec}
          </p>
          
          <div className="flex items-center space-x-4 text-xs text-slate-500 dark:text-slate-400">
            <div className="flex items-center space-x-1">
              <Clock className="h-3 w-3" />
              <span>Created {formatDate(integration.created_at)}</span>
            </div>
            
            {integration.ai_model_used && (
              <div className="flex items-center space-x-1">
                <Brain className="h-3 w-3" />
                <span>{integration.ai_model_used}</span>
              </div>
            )}
            
            {integration.processing_time_seconds && (
              <div className="flex items-center space-x-1">
                <Zap className="h-3 w-3" />
                <span>{integration.processing_time_seconds}s</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge className={getTypeColor(integration.integration_type)}>
            {integration.integration_type.toUpperCase()}
          </Badge>
          
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-700">
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Settings className="h-3 w-3 mr-1" />
            Configure
          </Button>
          
          <Button variant="outline" size="sm">
            <ExternalLink className="h-3 w-3 mr-1" />
            View Details
          </Button>
        </div>
        
        <div className="text-xs text-slate-500 dark:text-slate-400">
          ID: {integration.id.slice(0, 8)}...
        </div>
      </div>
    </motion.div>
  )
}
