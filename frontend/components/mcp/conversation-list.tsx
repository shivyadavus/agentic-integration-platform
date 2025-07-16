'use client'

import { motion } from 'framer-motion'
import { MessageSquare, MoreHorizontal, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/lib/utils'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: Message[]
}

interface ConversationListProps {
  conversations: Conversation[]
  activeConversationId: string | null
  onSelectConversation: (id: string) => void
  isLoading: boolean
}

export function ConversationList({
  conversations,
  activeConversationId,
  onSelectConversation,
  isLoading
}: ConversationListProps) {
  const getLastMessage = (conversation: Conversation) => {
    if (!conversation.messages || conversation.messages.length === 0) {
      return 'No messages yet'
    }
    const lastMessage = conversation.messages[conversation.messages.length - 1]
    return lastMessage.content.length > 50 
      ? `${lastMessage.content.substring(0, 50)}...`
      : lastMessage.content
  }

  const getMessageCount = (conversation: Conversation) => {
    return conversation.messages?.length || 0
  }

  if (isLoading) {
    return (
      <div className="flex-1 p-4 space-y-3">
        {[...Array(5)].map((_, i) => (
          <div
            key={`skeleton-${i}`}
            className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse"
          />
        ))}
      </div>
    )
  }

  if (conversations.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="text-center">
          <MessageSquare className="h-12 w-12 text-slate-400 mx-auto mb-3" />
          <p className="text-sm text-slate-500 dark:text-slate-400">
            No conversations yet
          </p>
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
            Start a new chat to begin
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {conversations.map((conversation, index) => {
        const isActive = conversation.id === activeConversationId
        const lastMessage = getLastMessage(conversation)
        const messageCount = getMessageCount(conversation)
        
        return (
          <motion.div
            key={conversation.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={cn(
              'group relative rounded-lg border p-3 cursor-pointer transition-all hover:shadow-md',
              isActive
                ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
                : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
            )}
            onClick={() => onSelectConversation(conversation.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <MessageSquare className={cn(
                    'h-4 w-4 flex-shrink-0',
                    isActive ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400'
                  )} />
                  <h3 className={cn(
                    'font-medium text-sm truncate',
                    isActive 
                      ? 'text-blue-900 dark:text-blue-100' 
                      : 'text-slate-900 dark:text-white'
                  )}>
                    {conversation.title}
                  </h3>
                </div>
                
                <p className={cn(
                  'text-xs line-clamp-2 mb-2',
                  isActive 
                    ? 'text-blue-700 dark:text-blue-300' 
                    : 'text-slate-500 dark:text-slate-400'
                )}>
                  {lastMessage}
                </p>
                
                <div className="flex items-center justify-between text-xs">
                  <span className={cn(
                    isActive 
                      ? 'text-blue-600 dark:text-blue-400' 
                      : 'text-slate-400 dark:text-slate-500'
                  )}>
                    {formatDate(conversation.updated_at)}
                  </span>
                  
                  {messageCount > 0 && (
                    <span className={cn(
                      'px-2 py-0.5 rounded-full text-xs font-medium',
                      isActive
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-200'
                        : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                    )}>
                      {messageCount}
                    </span>
                  )}
                </div>
              </div>
              
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => {
                  e.stopPropagation()
                  // TODO: Implement conversation options
                }}
              >
                <MoreHorizontal className="h-3 w-3" />
              </Button>
            </div>
            
            {/* Active indicator */}
            {isActive && (
              <motion.div
                layoutId="activeConversation"
                className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500 rounded-r-full"
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            )}
          </motion.div>
        )
      })}
    </div>
  )
}
