'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { Plus, X, Zap, MessageSquare, Sparkles, GitBranch } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FABAction {
  id: string
  label: string
  icon: React.ElementType
  color: string
  onClick: () => void
}

interface FloatingActionButtonProps {
  actions?: FABAction[]
  className?: string
  onPrimaryClick?: () => void
}

const defaultActions: FABAction[] = [
  {
    id: 'create',
    label: 'New Integration',
    icon: Plus,
    color: 'from-purple-500 to-pink-500',
    onClick: () => console.log('Create integration')
  },
  {
    id: 'deploy',
    label: 'Quick Deploy',
    icon: Zap,
    color: 'from-blue-500 to-cyan-500',
    onClick: () => console.log('Quick deploy')
  },
  {
    id: 'chat',
    label: 'AI Assistant',
    icon: MessageSquare,
    color: 'from-emerald-500 to-teal-500',
    onClick: () => console.log('Open chat')
  },
  {
    id: 'generate',
    label: 'Generate Code',
    icon: Sparkles,
    color: 'from-orange-500 to-red-500',
    onClick: () => console.log('Generate code')
  }
]

export function FloatingActionButton({ 
  actions = defaultActions, 
  className,
  onPrimaryClick 
}: FloatingActionButtonProps) {
  const [isOpen, setIsOpen] = useState(false)

  const toggleOpen = () => {
    if (onPrimaryClick && !isOpen) {
      onPrimaryClick()
    } else {
      setIsOpen(!isOpen)
    }
  }

  return (
    <div className={cn('fixed bottom-8 right-8 z-50', className)}>
      <div className="relative">
        {/* Action buttons */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute bottom-20 right-0 space-y-3"
            >
              {actions.map((action, index) => {
                const Icon = action.icon
                return (
                  <motion.div
                    key={action.id}
                    initial={{ scale: 0, y: 20, opacity: 0 }}
                    animate={{ 
                      scale: 1, 
                      y: 0, 
                      opacity: 1,
                      transition: {
                        type: "spring",
                        stiffness: 300,
                        damping: 20,
                        delay: index * 0.1
                      }
                    }}
                    exit={{ 
                      scale: 0, 
                      y: 20, 
                      opacity: 0,
                      transition: {
                        delay: (actions.length - index - 1) * 0.05
                      }
                    }}
                    whileHover={{ scale: 1.1, x: -5 }}
                    whileTap={{ scale: 0.95 }}
                    className="flex items-center justify-end space-x-3"
                  >
                    {/* Label */}
                    <motion.div
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }}
                      className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50 rounded-lg px-3 py-2 shadow-lg"
                    >
                      <span className="text-sm font-medium text-slate-900 dark:text-white whitespace-nowrap">
                        {action.label}
                      </span>
                    </motion.div>

                    {/* Action button */}
                    <motion.button
                      onClick={() => {
                        action.onClick()
                        setIsOpen(false)
                      }}
                      className={cn(
                        'w-12 h-12 rounded-full shadow-lg hover:shadow-xl flex items-center justify-center text-white transition-all duration-300',
                        `bg-gradient-to-r ${action.color}`
                      )}
                      whileHover={{ 
                        scale: 1.1,
                        boxShadow: "0 20px 40px rgba(0,0,0,0.3)"
                      }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <Icon className="w-5 h-5" />
                    </motion.button>
                  </motion.div>
                )
              })}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main FAB */}
        <motion.button
          onClick={toggleOpen}
          className="w-16 h-16 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600 rounded-2xl shadow-2xl hover:shadow-3xl flex items-center justify-center text-white transition-all duration-300 group overflow-hidden relative"
          whileHover={{ 
            scale: 1.05,
            boxShadow: "0 25px 50px rgba(168, 85, 247, 0.4)"
          }}
          whileTap={{ scale: 0.95 }}
          animate={{
            rotate: isOpen ? 45 : 0,
            borderRadius: isOpen ? '50%' : '1rem'
          }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
          {/* Shimmer effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-transparent to-white/20 -skew-x-12 translate-x-full group-hover:translate-x-[-200%] transition-transform duration-1000" />
          
          {/* Icon */}
          <motion.div
            animate={{ rotate: isOpen ? 45 : 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
          >
            {isOpen ? (
              <X className="w-7 h-7" />
            ) : (
              <Plus className="w-7 h-7" />
            )}
          </motion.div>

          {/* Pulse rings */}
          <motion.div
            className="absolute inset-0 border-2 border-purple-400 rounded-2xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.8, 0.3, 0.8],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute inset-0 border-2 border-pink-400 rounded-2xl"
            animate={{
              scale: [1, 1.4, 1],
              opacity: [0.6, 0.1, 0.6],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.5
            }}
          />
        </motion.button>
      </div>
    </div>
  )
}