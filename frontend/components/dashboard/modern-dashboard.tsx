'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Activity, Zap, CheckCircle, TrendingUp, Users, Server, Globe, Clock } from 'lucide-react'
import { StatsWidget } from '@/components/widgets/stats-widget'
import { ActivityWidget } from '@/components/widgets/activity-widget'
import { ChartWidget } from '@/components/widgets/chart-widget'
import { QuickActionsWidget } from '@/components/widgets/quick-actions-widget'

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

export function ModernDashboard() {
  const [refreshing, setRefreshing] = useState(false)

  const { data: integrations, isLoading, refetch, error } = useQuery({
    queryKey: ['integrations'],
    queryFn: async (): Promise<Integration[]> => {
      console.log('🚀 Fetching integrations from API...');
      const result = await api.integrations.list();
      console.log('✅ Integrations fetched:', result);
      console.log('✅ Number of integrations:', result?.length || 0);
      return result;
    },
    refetchInterval: 30000,
  })

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await refetch()
      // Show success toast
      const { toast } = await import('@/components/ui/toast')
      toast.success('Data Refreshed', 'Dashboard data has been updated successfully!')
    } catch (error) {
      const { toast } = await import('@/components/ui/toast')
      toast.error('Refresh Failed', 'Failed to refresh dashboard data')
    } finally {
      setTimeout(() => setRefreshing(false), 1000)
    }
  }

  const handleCreateIntegration = async () => {
    // This would typically navigate to the integration wizard
    const { toast } = await import('@/components/ui/toast')
    toast.info('Create Integration', 'Opening integration wizard...')
  }

  const handleViewAnalytics = async () => {
    const { toast } = await import('@/components/ui/toast')
    toast.info('Analytics', 'Opening detailed analytics view...')
  }

  // Debug logging
  console.log('Dashboard state:', { integrations, isLoading, error });
  console.log('Dashboard component rendered at:', new Date().toISOString());

  const totalIntegrations = integrations?.length || 0
  const activeIntegrations = integrations?.filter(i => i.status === 'active').length || 0
  const successRate = totalIntegrations > 0 ? Math.round((activeIntegrations / totalIntegrations) * 100) : 0

  // Mock chart data
  const integrationTrends = [
    { name: 'Mon', value: 12, change: 5 },
    { name: 'Tue', value: 18, change: 12 },
    { name: 'Wed', value: 15, change: -3 },
    { name: 'Thu', value: 22, change: 15 },
    { name: 'Fri', value: 28, change: 18 },
    { name: 'Sat', value: 20, change: 8 },
    { name: 'Sun', value: 24, change: 10 }
  ]

  const performanceData = [
    { name: 'Week 1', value: 85 },
    { name: 'Week 2', value: 92 },
    { name: 'Week 3', value: 78 },
    { name: 'Week 4', value: 96 },
    { name: 'Week 5', value: 89 },
    { name: 'Week 6', value: 94 }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50/50 via-transparent to-blue-50/30 dark:from-slate-950/50 dark:via-transparent dark:to-slate-900/50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <h1 className="text-4xl font-black bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 bg-clip-text text-transparent">
            Integration Analytics Hub
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Real-time insights and AI-powered integration management at your fingertips
          </p>
        </motion.div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsWidget
            title="Total Integrations [DEBUG]"
            value={`${totalIntegrations} (API: ${integrations?.length || 'null'})`}
            change={12}
            trend="up"
            icon={Activity}
            color="blue"
            subtitle={`${activeIntegrations} active, Loading: ${isLoading}`}
          />
          
          <StatsWidget
            title="Active Workflows"
            value={activeIntegrations}
            change={8}
            trend="up"
            icon={CheckCircle}
            color="green"
            subtitle="Currently running"
            progress={75}
          />
          
          <StatsWidget
            title="Success Rate"
            value={`${successRate}%`}
            change={2.1}
            trend="up"
            icon={TrendingUp}
            color="purple"
            subtitle="Integration reliability"
          />
          
          <StatsWidget
            title="Avg Response Time"
            value="2.3s"
            change={-0.5}
            trend="up"
            icon={Zap}
            color="orange"
            subtitle="Lightning fast processing"
          />
        </div>

        {/* Secondary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsWidget
            title="API Calls Today"
            value="1,247"
            change={15}
            trend="up"
            icon={Server}
            color="green"
            progress={82}
          />
          
          <StatsWidget
            title="Global Users"
            value="8,492"
            change={23}
            trend="up"
            icon={Users}
            color="blue"
          />
          
          <StatsWidget
            title="Uptime"
            value="99.9%"
            change={0.1}
            trend="up"
            icon={Globe}
            color="purple"
            subtitle="30-day average"
          />
        </div>

        {/* Charts and Widgets Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Integration Trends Chart */}
          <div className="lg:col-span-2">
            <ChartWidget
              title="Integration Trends"
              data={integrationTrends}
              type="area"
              color="purple"
            />
          </div>

          {/* Quick Actions */}
          <QuickActionsWidget />
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Chart */}
          <ChartWidget
            title="System Performance"
            data={performanceData}
            type="line"
            color="blue"
          />

          {/* Recent Activity */}
          <ActivityWidget />
        </div>

        {/* Additional Insights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-cyan-500/10 dark:from-purple-500/20 dark:via-blue-500/20 dark:to-cyan-500/20 rounded-3xl p-8 border border-purple-200/30 dark:border-purple-700/30"
        >
          <div className="text-center space-y-4">
            <div className="inline-flex items-center space-x-2 bg-white/80 dark:bg-slate-900/80 rounded-full px-6 py-3 backdrop-blur-sm">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                All Systems Operational
              </span>
            </div>
            
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white">
              AI-Powered Integration Platform
            </h3>
            
            <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              Experience the future of workflow automation with our intelligent integration platform. 
              Advanced AI models, real-time monitoring, and seamless deployment - all in one place.
            </p>

            <div className="flex justify-center space-x-6 pt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">50+</div>
                <div className="text-sm text-slate-500 dark:text-slate-400">AI Models</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">99.9%</div>
                <div className="text-sm text-slate-500 dark:text-slate-400">Uptime SLA</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">24/7</div>
                <div className="text-sm text-slate-500 dark:text-slate-400">Support</div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}