'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { RefreshCw, Plus, Filter, Activity, Zap, CheckCircle, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

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

export function Dashboard() {
  const [refreshing, setRefreshing] = useState(false)
  const [filter, setFilter] = useState<string>('all')

  const { data: integrations, isLoading, refetch } = useQuery({
    queryKey: ['integrations'],
    queryFn: async (): Promise<Integration[]> => {
      const response = await fetch('http://localhost:8000/api/v1/integrations/')
      if (!response.ok) {
        throw new Error('Failed to fetch integrations')
      }
      return response.json()
    },
    refetchInterval: 30000,
  })

  const handleRefresh = async () => {
    setRefreshing(true)
    await refetch()
    setTimeout(() => setRefreshing(false), 1000)
  }

  const filteredIntegrations = integrations?.filter(integration => {
    if (filter === 'all') return true
    return integration.status === filter
  }) || []

  const statusCounts = integrations?.reduce((acc, integration) => {
    acc[integration.status] = (acc[integration.status] || 0) + 1
    return acc
  }, {} as Record<string, number>) || {}

  const totalIntegrations = integrations?.length || 0
  const activeIntegrations = statusCounts.active || 0

  return (
    <div className="h-full overflow-auto bg-gradient-to-br from-slate-50/50 via-transparent to-blue-50/50 dark:from-slate-950/50 dark:via-transparent dark:to-slate-900/50" data-testid="dashboard">
      <div className="p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Integration Dashboard
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2">
              Monitor and manage your AI-powered integrations
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <Button
              onClick={handleRefresh}
              disabled={refreshing}
              variant="outline"
              className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm"
            >
              <RefreshCw className={cn('h-4 w-4 mr-2', refreshing && 'animate-spin')} />
              Refresh
            </Button>
            
            <Button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600">
              <Plus className="h-4 w-4 mr-2" />
              New Integration
            </Button>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6 shadow-lg"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-xl">
                <Activity className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <span className="text-xs text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20 px-2 py-1 rounded-full">
                +12%
              </span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {totalIntegrations}
              </div>
              <div className="text-sm font-medium text-slate-900 dark:text-white">
                Total Integrations
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">
                All time integrations
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6 shadow-lg"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-xl">
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <span className="text-xs text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20 px-2 py-1 rounded-full">
                +8%
              </span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {activeIntegrations}
              </div>
              <div className="text-sm font-medium text-slate-900 dark:text-white">
                Active Integrations
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">
                Currently running
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6 shadow-lg"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-emerald-100 dark:bg-emerald-900/20 rounded-xl">
                <TrendingUp className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
              </div>
              <span className="text-xs text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20 px-2 py-1 rounded-full">
                +2.1%
              </span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                98<span className="text-sm">%</span>
              </div>
              <div className="text-sm font-medium text-slate-900 dark:text-white">
                Success Rate
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">
                Integration success
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6 shadow-lg"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-xl">
                <Zap className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <span className="text-xs text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20 px-2 py-1 rounded-full">
                -0.5s
              </span>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                2.3<span className="text-sm">s</span>
              </div>
              <div className="text-sm font-medium text-slate-900 dark:text-white">
                Avg Processing
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">
                Processing time
              </div>
            </div>
          </motion.div>
        </div>

        {/* Integrations List */}
        <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              Recent Integrations
            </h2>
            <div className="flex items-center space-x-3">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="text-sm bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2"
              >
                <option value="all">All Status</option>
                <option value="draft">Draft</option>
                <option value="generating">Generating</option>
                <option value="ready">Ready</option>
                <option value="active">Active</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>

          {isLoading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-24 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse"
                />
              ))}
            </div>
          ) : filteredIntegrations.length === 0 ? (
            <div className="text-center py-12">
              <Plus className="h-16 w-16 text-slate-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                No integrations found
              </h3>
              <p className="text-slate-500 dark:text-slate-400 mb-6">
                Get started by creating your first integration
              </p>
              <Button className="bg-gradient-to-r from-purple-500 to-blue-500">
                <Plus className="h-4 w-4 mr-2" />
                Create Integration
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredIntegrations.map((integration, index) => (
                <motion.div
                  key={integration.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200/50 dark:border-slate-700/50 hover:shadow-md transition-all duration-200"
                  data-testid="integration-card"
                  data-name={integration.name}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-slate-900 dark:text-white">
                        {integration.name}
                      </h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                        {integration.natural_language_spec.substring(0, 100)}...
                      </p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-slate-500">
                        <span>Type: {integration.integration_type}</span>
                        <span>Created: {new Date(integration.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={cn(
                        'px-3 py-1 rounded-full text-xs font-medium',
                        integration.status === 'active' && 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
                        integration.status === 'draft' && 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300',
                        integration.status === 'generating' && 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300',
                        integration.status === 'error' && 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
                      )}>
                        {integration.status}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
