'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { NotificationDropdown } from '@/components/ui/notification-dropdown'
import { SearchModal } from '@/components/ui/search-modal'
import {
  Search,
  Settings,
  User,
  Menu,
  Activity,
  Zap
} from 'lucide-react'
import { motion } from 'framer-motion'

interface HeaderProps {
  activeView: string
  onViewChange: (view: string) => void
  sidebarOpen: boolean
  onSidebarToggle: () => void
}

export function Header({
  activeView,
  onViewChange,
  sidebarOpen,
  onSidebarToggle
}: HeaderProps) {
  const [searchOpen, setSearchOpen] = useState(false)

  // Global keyboard shortcut for search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setSearchOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])
  const getViewTitle = () => {
    switch (activeView) {
      case 'dashboard':
        return 'Integration Dashboard'
      case 'create':
        return 'Create New Integration'
      case 'chat':
        return 'MCP Agent Chat'
      case 'knowledge':
        return 'Knowledge Graph Explorer'
      default:
        return 'Agentic Integration Platform'
    }
  }

  const getViewDescription = () => {
    switch (activeView) {
      case 'dashboard':
        return 'Monitor and manage your integrations'
      case 'create':
        return 'Build AI-powered integrations with natural language'
      case 'chat':
        return 'Converse with the MCP agent for integration assistance'
      case 'knowledge':
        return 'Explore integration patterns and relationships'
      default:
        return 'AI-powered B2B software integration platform'
    }
  }

  return (
    <header className="relative bg-white/90 dark:bg-slate-950/90 backdrop-blur-xl border-b border-slate-200/50 dark:border-slate-800/50 px-6 py-4 shadow-sm">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 via-transparent to-blue-500/5 pointer-events-none" />

      <div className="relative flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center space-x-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={onSidebarToggle}
            className="lg:hidden h-10 w-10 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Menu className="h-5 w-5" />
          </Button>

          <motion.div
            key={activeView}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
            className="space-y-1"
          >
            <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
              {getViewTitle()}
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400 font-medium">
              {getViewDescription()}
            </p>
          </motion.div>
        </div>

        {/* Center Section - Status Indicators */}
        <div className="hidden md:flex items-center space-x-3">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-950/20 dark:to-green-950/20 rounded-xl border border-emerald-200/50 dark:border-emerald-800/50 shadow-sm"
          >
            <div className="relative">
              <Activity className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            </div>
            <span className="text-sm font-semibold text-emerald-700 dark:text-emerald-300">
              System Online
            </span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 rounded-xl border border-blue-200/50 dark:border-blue-800/50 shadow-sm"
          >
            <Zap className="h-4 w-4 text-blue-600 dark:text-blue-400 animate-pulse" />
            <span className="text-sm font-semibold text-blue-700 dark:text-blue-300">
              AI Ready
            </span>
          </motion.div>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSearchOpen(true)}
            className="relative h-10 w-10 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-200"
            title="Search (⌘K)"
          >
            <Search className="h-5 w-5" />
          </Button>

          <NotificationDropdown />

          <ThemeToggle />

          <Button
            variant="ghost"
            size="icon"
            className="h-10 w-10 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-200"
          >
            <Settings className="h-5 w-5" />
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="h-10 w-10 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-200"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
              <User className="h-4 w-4 text-white" />
            </div>
          </Button>
        </div>
      </div>

      {/* Search Modal */}
      <SearchModal
        isOpen={searchOpen}
        onClose={() => setSearchOpen(false)}
      />
    </header>
  )
}
