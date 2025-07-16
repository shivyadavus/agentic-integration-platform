'use client'

import { motion } from 'framer-motion'
import { User, Bot, Copy, ThumbsUp, ThumbsDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/lib/utils'
import { useState } from 'react'
import toast from 'react-hot-toast'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      toast.success('Message copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      toast.error('Failed to copy message')
    }
  }

  const formatMessageContent = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-sm">$1</code>')
      .replace(/\n/g, '<br>')
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} space-x-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : 'bg-gradient-to-br from-purple-500 to-indigo-600 text-white'
          }`}>
            {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
          </div>
        </div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white'
          }`}>
            <div 
              className="text-sm leading-relaxed"
              dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
            />
          </div>

          {/* Message Actions */}
          <div className={`flex items-center space-x-2 mt-2 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              {formatDate(message.timestamp)}
            </span>

            {!isUser && (
              <div className="flex items-center space-x-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={handleCopy}
                >
                  <Copy className={`h-3 w-3 ${copied ? 'text-green-500' : 'text-slate-400'}`} />
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                >
                  <ThumbsUp className="h-3 w-3 text-slate-400 hover:text-green-500" />
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                >
                  <ThumbsDown className="h-3 w-3 text-slate-400 hover:text-red-500" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
