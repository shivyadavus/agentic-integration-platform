'use client'

import { motion } from 'framer-motion'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ChartWidgetProps {
  title: string
  data?: Array<{ name: string; value: number; change?: number }>
  type?: 'line' | 'area'
  color?: 'blue' | 'green' | 'purple' | 'orange'
  className?: string
  showTrend?: boolean
}

const defaultData = [
  { name: 'Mon', value: 120, change: 5 },
  { name: 'Tue', value: 190, change: 12 },
  { name: 'Wed', value: 150, change: -3 },
  { name: 'Thu', value: 220, change: 15 },
  { name: 'Fri', value: 280, change: 18 },
  { name: 'Sat', value: 200, change: 8 },
  { name: 'Sun', value: 240, change: 10 }
]

const colorMap = {
  blue: {
    stroke: '#3b82f6',
    fill: 'url(#blueGradient)',
    bg: 'from-blue-500/10 to-cyan-500/10 dark:from-blue-500/20 dark:to-cyan-500/20'
  },
  green: {
    stroke: '#10b981',
    fill: 'url(#greenGradient)',
    bg: 'from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20'
  },
  purple: {
    stroke: '#8b5cf6',
    fill: 'url(#purpleGradient)',
    bg: 'from-purple-500/10 to-pink-500/10 dark:from-purple-500/20 dark:to-pink-500/20'
  },
  orange: {
    stroke: '#f97316',
    fill: 'url(#orangeGradient)',
    bg: 'from-orange-500/10 to-red-500/10 dark:from-orange-500/20 dark:to-red-500/20'
  }
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50 rounded-xl p-3 shadow-xl">
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{`${label}`}</p>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Value: <span className="font-semibold text-purple-600 dark:text-purple-400">{payload[0].value}</span>
        </p>
      </div>
    )
  }
  return null
}

export function ChartWidget({
  title,
  data = defaultData,
  type = 'area',
  color = 'purple',
  className,
  showTrend = true
}: ChartWidgetProps) {
  const colors = colorMap[color]
  const totalValue = data.reduce((sum, item) => sum + item.value, 0)
  const avgChange = data.reduce((sum, item) => sum + (item.change || 0), 0) / data.length

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className={className}
    >
      <Card className={cn(
        'h-full bg-gradient-to-br backdrop-blur-sm border border-slate-200/30 dark:border-slate-700/30 shadow-xl',
        colors.bg
      )}>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-bold">{title}</CardTitle>
            {showTrend && (
              <Badge variant="secondary" className="text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/30">
                <TrendingUp className="h-3 w-3 mr-1" />
                +{avgChange.toFixed(1)}%
              </Badge>
            )}
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {totalValue.toLocaleString()}
          </div>
        </CardHeader>
        
        <CardContent className="pt-0">
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              {type === 'area' ? (
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
                    </linearGradient>
                    <linearGradient id="greenGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.05}/>
                    </linearGradient>
                    <linearGradient id="purpleGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.05}/>
                    </linearGradient>
                    <linearGradient id="orangeGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f97316" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#f97316" stopOpacity={0.05}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.3} />
                  <XAxis 
                    dataKey="name" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#64748b' }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#64748b' }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke={colors.stroke}
                    strokeWidth={3}
                    fill={colors.fill}
                    fillOpacity={1}
                  />
                </AreaChart>
              ) : (
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.3} />
                  <XAxis 
                    dataKey="name" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#64748b' }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#64748b' }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke={colors.stroke}
                    strokeWidth={3}
                    dot={{ fill: colors.stroke, strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: colors.stroke, strokeWidth: 2 }}
                  />
                </LineChart>
              )}
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}