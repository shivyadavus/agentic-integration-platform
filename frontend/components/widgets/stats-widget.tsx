'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'

interface StatsWidgetProps {
  title: string
  value: string | number
  change?: number
  trend?: 'up' | 'down' | 'neutral'
  icon?: React.ElementType
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red'
  progress?: number
  subtitle?: string
  className?: string
}

const colorMap = {
  blue: {
    bg: 'from-blue-500/10 to-cyan-500/10 dark:from-blue-500/20 dark:to-cyan-500/20',
    icon: 'bg-gradient-to-br from-blue-500 to-cyan-600',
    text: 'from-blue-600 to-cyan-600',
    border: 'border-blue-200/50 dark:border-blue-700/50'
  },
  green: {
    bg: 'from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20',
    icon: 'bg-gradient-to-br from-emerald-500 to-teal-600',
    text: 'from-emerald-600 to-teal-600',
    border: 'border-emerald-200/50 dark:border-emerald-700/50'
  },
  purple: {
    bg: 'from-purple-500/10 to-pink-500/10 dark:from-purple-500/20 dark:to-pink-500/20',
    icon: 'bg-gradient-to-br from-purple-500 to-pink-600',
    text: 'from-purple-600 to-pink-600',
    border: 'border-purple-200/50 dark:border-purple-700/50'
  },
  orange: {
    bg: 'from-orange-500/10 to-red-500/10 dark:from-orange-500/20 dark:to-red-500/20',
    icon: 'bg-gradient-to-br from-orange-500 to-red-600',
    text: 'from-orange-600 to-red-600',
    border: 'border-orange-200/50 dark:border-orange-700/50'
  },
  red: {
    bg: 'from-red-500/10 to-pink-500/10 dark:from-red-500/20 dark:to-pink-500/20',
    icon: 'bg-gradient-to-br from-red-500 to-pink-600',
    text: 'from-red-600 to-pink-600',
    border: 'border-red-200/50 dark:border-red-700/50'
  }
}

export function StatsWidget({
  title,
  value,
  change,
  trend = 'neutral',
  icon: Icon,
  color = 'blue',
  progress,
  subtitle,
  className
}: StatsWidgetProps) {
  const colors = colorMap[color]
  
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-3 w-3" />
      case 'down':
        return <TrendingDown className="h-3 w-3" />
      default:
        return <Minus className="h-3 w-3" />
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/30'
      case 'down':
        return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30'
      default:
        return 'text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-900/30'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ duration: 0.3 }}
      className={className}
    >
      <Card className={cn(
        'relative overflow-hidden backdrop-blur-sm border shadow-xl hover:shadow-2xl transition-all duration-500 group',
        `bg-gradient-to-br ${colors.bg}`,
        colors.border
      )}>
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        
        <CardContent className="p-6 relative z-10">
          <div className="flex items-start justify-between mb-4">
            {Icon && (
              <div className={cn(
                'p-3 rounded-2xl shadow-lg',
                colors.icon
              )}>
                <Icon className="h-6 w-6 text-white" />
              </div>
            )}
            
            {change !== undefined && (
              <Badge variant="secondary" className={cn(
                'px-3 py-1 rounded-full text-xs font-semibold',
                getTrendColor()
              )}>
                <div className="flex items-center space-x-1">
                  {getTrendIcon()}
                  <span>{change > 0 ? '+' : ''}{change}%</span>
                </div>
              </Badge>
            )}
          </div>

          <div className="space-y-2">
            <div className={cn(
              'text-4xl font-black bg-gradient-to-r bg-clip-text text-transparent',
              colors.text
            )}>
              {value}
            </div>
            
            <div className="text-lg font-bold text-slate-900 dark:text-white">
              {title}
            </div>
            
            {subtitle && (
              <div className="text-sm text-slate-600 dark:text-slate-400">
                {subtitle}
              </div>
            )}
            
            {progress !== undefined && (
              <div className="pt-2">
                <Progress value={progress} className="h-2" />
                <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {progress}% complete
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}