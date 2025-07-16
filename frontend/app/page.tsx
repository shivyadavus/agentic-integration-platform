'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Dashboard } from '@/components/dashboard/dashboard-simple'
import { IntegrationWizard } from '@/components/integration/integration-wizard'
import { MCPChat } from '@/components/mcp/mcp-chat'
import { KnowledgeGraph } from '@/components/knowledge/knowledge-graph'
import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'
import { Plus, MessageSquare, Network, BarChart3, Sparkles } from 'lucide-react'

type ActiveView = 'dashboard' | 'create' | 'chat' | 'knowledge'

export default function Home() {
  const [activeView, setActiveView] = useState<ActiveView>('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const renderActiveView = () => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard />
      case 'create':
        return <IntegrationWizard onComplete={() => setActiveView('dashboard')} />
      case 'chat':
        return <MCPChat />
      case 'knowledge':
        return <KnowledgeGraph />
      default:
        return <Dashboard />
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
    <div className="flex h-screen overflow-hidden" data-testid="app-ready">
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
        
        {/* Additional ambient orbs */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            repeatType: "reverse"
          }}
          className="absolute top-3/4 left-1/6 w-32 h-32 bg-gradient-to-r from-amber-400/15 to-orange-400/15 rounded-full blur-2xl"
        />
        <motion.div
          animate={{
            scale: [1, 0.8, 1],
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            repeatType: "reverse",
            delay: 3
          }}
          className="absolute bottom-1/6 left-1/2 w-40 h-40 bg-gradient-to-r from-violet-400/15 to-purple-400/15 rounded-full blur-2xl"
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

          {/* Enhanced Floating Action Elements */}
          <motion.div
            initial={{ opacity: 0, scale: 0, rotate: -180 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ 
              delay: 1, 
              duration: 0.8, 
              type: "spring",
              stiffness: 200,
              damping: 15
            }}
            className="fixed bottom-8 right-8 z-50"
          >
            <div className="flex flex-col space-y-4">
              <motion.button
                whileHover={{ 
                  scale: 1.15, 
                  rotate: 5,
                  boxShadow: "0 20px 40px rgba(168, 85, 247, 0.4)"
                }}
                whileTap={{ scale: 0.9 }}
                animate={{
                  boxShadow: [
                    "0 10px 20px rgba(168, 85, 247, 0.2)",
                    "0 15px 30px rgba(168, 85, 247, 0.3)",
                    "0 10px 20px rgba(168, 85, 247, 0.2)"
                  ]
                }}
                transition={{
                  boxShadow: {
                    duration: 2,
                    repeat: Infinity,
                    repeatType: "reverse"
                  }
                }}
                className="relative w-16 h-16 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600 rounded-2xl shadow-2xl flex items-center justify-center text-white transition-all duration-300 group overflow-hidden"
                onClick={() => setActiveView('create')}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-transparent to-white/20 -skew-x-12 translate-x-full group-hover:translate-x-[-200%] transition-transform duration-1000" />
                <Plus className="w-7 h-7 relative z-10" />
              </motion.button>

              <motion.button
                whileHover={{ 
                  scale: 1.15, 
                  rotate: -5,
                  boxShadow: "0 15px 30px rgba(16, 185, 129, 0.4)"
                }}
                whileTap={{ scale: 0.9 }}
                animate={{
                  rotate: [0, 5, 0, -5, 0],
                }}
                transition={{
                  rotate: {
                    duration: 6,
                    repeat: Infinity,
                    repeatType: "reverse"
                  }
                }}
                className="relative w-14 h-14 bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 rounded-2xl shadow-xl flex items-center justify-center text-white transition-all duration-300 group overflow-hidden"
                onClick={() => setActiveView('chat')}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-transparent to-white/20 -skew-x-12 translate-x-full group-hover:translate-x-[-200%] transition-transform duration-1000" />
                <Sparkles className="w-5 h-5 relative z-10 animate-pulse" />
              </motion.button>
            </div>
          </motion.div>
        </main>
      </div>
    </div>
  )
}