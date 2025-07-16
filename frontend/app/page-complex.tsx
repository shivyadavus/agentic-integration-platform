'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ModernDashboard } from '@/components/dashboard/modern-dashboard'
import { IntegrationWizard } from '@/components/integration/integration-wizard'
import { MCPChat } from '@/components/mcp/mcp-chat'
import { KnowledgeGraph } from '@/components/knowledge/knowledge-graph'
import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'
import { Plus, MessageSquare, Network, BarChart3, Sparkles } from 'lucide-react'
import { FloatingActionButton } from '@/components/ui/floating-action-button'

type ActiveView = 'dashboard' | 'create' | 'chat' | 'knowledge'

export default function Home() {
  const [activeView, setActiveView] = useState<ActiveView>('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const renderActiveView = () => {
    switch (activeView) {
      case 'dashboard':
        return <ModernDashboard />
      case 'create':
        return <IntegrationWizard onComplete={() => setActiveView('dashboard')} />
      case 'chat':
        return <MCPChat />
      case 'knowledge':
        return <KnowledgeGraph />
      default:
        return <ModernDashboard />
    }
  }

  const navigationItems = [
    {
      id: 'dashboard' as const,
      label: 'Dashboard',
      icon: BarChart3,
      description: 'Overview & Analytics',
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'create' as const,
      label: 'Create Integration',
      icon: Plus,
      description: 'Build with AI',
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      id: 'chat' as const,
      label: 'AI Assistant',
      icon: MessageSquare,
      description: 'Smart Conversations',
      gradient: 'from-emerald-500 to-teal-500'
    },
    {
      id: 'knowledge' as const,
      label: 'Knowledge Graph',
      icon: Network,
      description: 'Explore Patterns',
      gradient: 'from-orange-500 to-red-500'
    }
  ]

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Enhanced Animated Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-100/30 dark:from-slate-950 dark:via-slate-900 dark:to-slate-800" />

        {/* Advanced floating orbs with motion */}
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: "reverse"
          }}
          className="absolute top-1/4 left-1/4 w-64 h-64 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, -80, 0],
            y: [0, 60, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            repeatType: "reverse",
            delay: 2
          }}
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, 60, 0],
            y: [0, -80, 0],
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            repeatType: "reverse",
            delay: 4
          }}
          className="absolute top-1/2 right-1/3 w-48 h-48 bg-gradient-to-r from-emerald-400/20 to-teal-400/20 rounded-full blur-3xl"
        />
      </div>

      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        activeView={activeView}
        onViewChange={(view: string) => setActiveView(view as ActiveView)}
        navigationItems={navigationItems}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header
          activeView={activeView}
          onViewChange={(view: string) => setActiveView(view as ActiveView)}
          sidebarOpen={sidebarOpen}
          onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}
        />

        <main className="flex-1 overflow-hidden relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeView}
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 1.05, y: -20 }}
              transition={{
                duration: 0.4,
                ease: [0.4, 0, 0.2, 1],
                scale: { duration: 0.3 }
              }}
              className="h-full"
            >
              {renderActiveView()}
            </motion.div>
          </AnimatePresence>

          {/* Enhanced Floating Action Button */}
          <FloatingActionButton
            actions={[
              {
                id: 'create',
                label: 'New Integration',
                icon: Plus,
                color: 'from-purple-500 to-pink-500',
                onClick: () => setActiveView('create')
              },
              {
                id: 'chat',
                label: 'AI Assistant',
                icon: MessageSquare,
                color: 'from-emerald-500 to-teal-500',
                onClick: () => setActiveView('chat')
              },
              {
                id: 'knowledge',
                label: 'Knowledge Graph',
                icon: Network,
                color: 'from-orange-500 to-red-500',
                onClick: () => setActiveView('knowledge')
              },
              {
                id: 'generate',
                label: 'Generate Code',
                icon: Sparkles,
                color: 'from-blue-500 to-cyan-500',
                onClick: () => setActiveView('create')
              }
            ]}
          />
        </main>
      </div>
    </div>
  )
}