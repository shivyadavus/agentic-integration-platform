'use client'

import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { ChevronLeft, ChevronRight, Sparkles } from 'lucide-react'

interface NavigationItem {
  id: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  description: string
  gradient?: string
}

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
  activeView: string
  onViewChange: (view: string) => void
  navigationItems: NavigationItem[]
}

export function Sidebar({
  isOpen,
  onToggle,
  activeView,
  onViewChange,
  navigationItems
}: SidebarProps) {
  return (
    <motion.div
      initial={false}
      animate={{ width: isOpen ? 320 : 80 }}
      transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
      className="relative bg-white/90 dark:bg-slate-950/90 backdrop-blur-xl border-r border-slate-200/50 dark:border-slate-800/50 flex flex-col shadow-2xl"
    >
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-purple-500/5 via-transparent to-blue-500/5 pointer-events-none" />

      {/* Header */}
      <div className="relative p-6 border-b border-slate-200/50 dark:border-slate-800/50">
        <div className="flex items-center justify-between">
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="flex items-center space-x-3"
            >
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 via-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full border-2 border-white dark:border-slate-950 animate-pulse" />
              </div>
              <div>
                <h1 className="font-bold text-lg bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
                  Agentic Platform
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
                  AI Integration Hub
                </p>
              </div>
            </motion.div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="h-10 w-10 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-200"
          >
            {isOpen ? (
              <ChevronLeft className="h-5 w-5" />
            ) : (
              <ChevronRight className="h-5 w-5" />
            )}
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-6 space-y-3 relative">
        {navigationItems.map((item, index) => {
          const Icon = item.icon
          const isActive = activeView === item.id

          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative"
            >
              <Button
                variant="ghost"
                data-testid={`nav-${item.id}`}
                className={cn(
                  'w-full h-14 relative overflow-hidden transition-all duration-300 group',
                  isActive
                    ? 'bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-200/50 dark:border-purple-800/50 shadow-lg'
                    : 'hover:bg-slate-100/50 dark:hover:bg-slate-800/50',
                  !isOpen && 'justify-center px-0',
                  isOpen && 'justify-start px-4'
                )}
                onClick={() => onViewChange(item.id)}
              >
                {/* Background gradient for active state */}
                {isActive && (
                  <motion.div
                    layoutId="activeBackground"
                    className={cn(
                      'absolute inset-0 bg-gradient-to-r opacity-10 rounded-xl',
                      item.gradient || 'from-purple-500 to-blue-500'
                    )}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}

                {/* Icon container */}
                <div className={cn(
                  'relative flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-300',
                  isActive
                    ? `bg-gradient-to-r ${item.gradient || 'from-purple-500 to-blue-500'} text-white shadow-lg`
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 group-hover:bg-slate-200 dark:group-hover:bg-slate-700',
                  !isOpen && 'mx-auto'
                )}>
                  <Icon className="h-5 w-5" />
                </div>

                {/* Text content */}
                {isOpen && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    transition={{ duration: 0.2 }}
                    className="flex flex-col items-start ml-3 flex-1"
                  >
                    <span className={cn(
                      'font-semibold text-sm',
                      isActive
                        ? 'text-slate-900 dark:text-white'
                        : 'text-slate-700 dark:text-slate-300'
                    )}>
                      {item.label}
                    </span>
                    <span className={cn(
                      'text-xs',
                      isActive
                        ? 'text-slate-600 dark:text-slate-400'
                        : 'text-slate-500 dark:text-slate-500'
                    )}>
                      {item.description}
                    </span>
                  </motion.div>
                )}

                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="absolute right-2 w-2 h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
              </Button>
            </motion.div>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="relative p-6 border-t border-slate-200/50 dark:border-slate-800/50">
        {isOpen ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.3 }}
            className="space-y-3"
          >
            <div className="flex items-center space-x-2 p-3 bg-gradient-to-r from-emerald-50 to-blue-50 dark:from-emerald-950/20 dark:to-blue-950/20 rounded-xl border border-emerald-200/50 dark:border-emerald-800/50">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-emerald-700 dark:text-emerald-300">
                System Online
              </span>
            </div>

            <div className="text-center space-y-1">
              <p className="text-xs font-semibold bg-gradient-to-r from-purple-600 to-blue-600 dark:from-purple-400 dark:to-blue-400 bg-clip-text text-transparent">
                Powered by AI & MCP
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                v2.0.0 • Latest
              </p>
            </div>
          </motion.div>
        ) : (
          <div className="flex justify-center">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
