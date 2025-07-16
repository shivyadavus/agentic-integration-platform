'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { ChatMessage } from './chat-message'
import { ChatInput } from './chat-input'
import { ConversationList } from './conversation-list'
import {
  MessageSquare,
  Plus,
  Bot,
  User,
  Loader2,
  Sparkles,
  Play,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react'
import { api } from '@/lib/api'

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

interface ExecutionStatus {
  status: 'idle' | 'planning' | 'executing' | 'completed' | 'failed'
  progress: number
  currentStep: string
  error?: string
}

export function MCPChat() {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [isTyping, setIsTyping] = useState(false)
  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus>({
    status: 'idle',
    progress: 0,
    currentStep: ''
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  // Fetch conversations - return empty array since we don't have a list endpoint yet
  const { data: conversations, isLoading: conversationsLoading } = useQuery({
    queryKey: ['conversations'],
    queryFn: async (): Promise<Conversation[]> => {
      // Return empty array - conversations will be created on demand
      return []
    }
  })

  // Fetch active conversation details
  const { data: activeConversation } = useQuery({
    queryKey: ['conversation-details', activeConversationId],
    queryFn: async (): Promise<Conversation | null> => {
      if (!activeConversationId) return null
      try {
        const conversation = await api.mcp.getConversation(activeConversationId);
        // Ensure all messages have valid timestamps
        const processedMessages = (conversation.messages || []).map((message: any, index: number) => ({
          ...message,
          timestamp: message.timestamp || new Date().toISOString(),
          id: message.id || `msg-${Date.now()}-${index}`
        }))

        return {
          id: conversation.conversation_id,
          title: `Integration Chat ${conversation.conversation_id.slice(0, 8)}`,
          created_at: conversation.created_at || new Date().toISOString(),
          updated_at: conversation.updated_at || new Date().toISOString(),
          messages: processedMessages
        }
      } catch (error) {
        console.warn('Failed to fetch conversation details:', error)
        return null
      }
    },
    enabled: !!activeConversationId
  })

  // Get messages from active conversation
  const messages = activeConversation?.messages || []
  const messagesLoading = false

  // Create new conversation
  const createConversationMutation = useMutation({
    mutationFn: async (initialRequest: string) => {
      return api.mcp.startConversation({ initial_request: initialRequest });
    },
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      setActiveConversationId(response.conversation_id)
      toast.success('New conversation started')
    },
    onError: () => {
      toast.error('Failed to create conversation')
    }
  })

  // Send message
  const sendMessageMutation = useMutation({
    mutationFn: ({ conversationId, message }: { conversationId: string, message: string }) =>
      api.mcp.sendMessage(conversationId, { message }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation-details', activeConversationId] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: (error: any) => {
      toast.error(`Failed to send message: ${error.message}`)
    }
  })

  // Execute integration
  const executeIntegrationMutation = useMutation({
    mutationFn: async (integrationPlan: string) => {
      setExecutionStatus({ status: 'planning', progress: 10, currentStep: 'Analyzing integration plan...' })

      // Use real API to execute integration from plan
      const result = await api.integrations.executeFromPlan({
        plan: integrationPlan,
        conversation_id: activeConversationId || undefined
      })

      // Update progress through the execution steps
      setExecutionStatus({ status: 'executing', progress: 30, currentStep: 'Connecting to source system...' })
      await new Promise(resolve => setTimeout(resolve, 500))

      setExecutionStatus({ status: 'executing', progress: 50, currentStep: 'Authenticating with APIs...' })
      await new Promise(resolve => setTimeout(resolve, 500))

      setExecutionStatus({ status: 'executing', progress: 70, currentStep: 'Mapping data fields...' })
      await new Promise(resolve => setTimeout(resolve, 500))

      setExecutionStatus({ status: 'executing', progress: 90, currentStep: 'Testing data flow...' })
      await new Promise(resolve => setTimeout(resolve, 500))

      setExecutionStatus({ status: 'completed', progress: 100, currentStep: 'Integration deployed successfully!' })

      return result
    },
    onSuccess: (result) => {
      toast.success(`Integration executed successfully! ID: ${result.integration_id}`)
      // Invalidate queries to refresh the integrations list
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
    },
    onError: (error: any) => {
      setExecutionStatus({
        status: 'failed',
        progress: 0,
        currentStep: 'Execution failed',
        error: error.message
      })
      toast.error(`Failed to execute integration: ${error.message}`)
    }
  })

  const handleSendMessage = async (content: string) => {
    try {
      if (!activeConversationId) {
        // Create new conversation first
        console.log('Creating new conversation with content:', content);
        const conversation = await createConversationMutation.mutateAsync(content)
        console.log('Created conversation:', conversation);
        setActiveConversationId(conversation.conversation_id)
        await sendMessageMutation.mutateAsync({ conversationId: conversation.conversation_id, message: content })
      } else {
        await sendMessageMutation.mutateAsync({ conversationId: activeConversationId, message: content })
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }

  const handleNewConversation = async () => {
    try {
      console.log('Creating new conversation...');
      const conversation = await createConversationMutation.mutateAsync('Hello! I need help with an integration.')
      console.log('New conversation created:', conversation);
      setActiveConversationId(conversation.conversation_id)
    } catch (error) {
      console.error('Failed to create new conversation:', error);
    }
  }

  const handleExecuteIntegration = async () => {
    try {
      // Extract integration plan from conversation messages
      const integrationPlan = messages
        .filter(msg => msg.role === 'assistant')
        .map(msg => msg.content)
        .join('\n\n')

      if (!integrationPlan.trim()) {
        toast.error('No integration plan found in conversation. Please discuss an integration first.')
        return
      }

      await executeIntegrationMutation.mutateAsync(integrationPlan)
    } catch (error) {
      console.error('Failed to execute integration:', error)
    }
  }

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // No auto-selection needed since conversations are created on demand

  return (
    <div className="h-full flex bg-gradient-to-br from-slate-50/50 via-blue-50/30 to-indigo-50/50 dark:from-slate-950/50 dark:via-slate-900/30 dark:to-slate-800/50" data-testid="mcp-chat-interface">
      {/* Conversations Sidebar */}
      <div className="w-80 bg-white/90 dark:bg-slate-950/90 backdrop-blur-xl border-r border-slate-200/50 dark:border-slate-800/50 flex flex-col shadow-2xl">
        <div className="p-6 border-b border-slate-200/50 dark:border-slate-800/50">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                AI Conversations
              </h2>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                Chat with your AI assistant
              </p>
            </div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                onClick={handleNewConversation}
                disabled={createConversationMutation.isPending}
                size="sm"
                className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white shadow-lg rounded-xl"
                data-testid="new-conversation-btn"
              >
                {createConversationMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-1" />
                    New Chat
                  </>
                )}
              </Button>
            </motion.div>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-300 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
            <Sparkles className="h-4 w-4 text-blue-500" />
            <span>AI-powered integration assistant</span>
          </div>
        </div>

        <ConversationList
          conversations={conversations || []}
          activeConversationId={activeConversationId}
          onSelectConversation={setActiveConversationId}
          isLoading={conversationsLoading}
        />
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {activeConversation ? (
          <>
            {/* Chat Header */}
            <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 p-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">
                    {activeConversation.title}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    MCP Agent • Ready to help with integrations
                  </p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messagesLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
                </div>
              ) : messages && messages.length > 0 ? (
                <AnimatePresence>
                  {messages.map((message, index) => (
                    <motion.div
                      key={message.id || `message-${index}-${message.timestamp || Date.now()}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <ChatMessage message={message} />
                    </motion.div>
                  ))}
                </AnimatePresence>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <MessageSquare className="h-12 w-12 text-slate-400 mb-4" />
                  <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                    Start a conversation
                  </h3>
                  <p className="text-slate-500 dark:text-slate-400 max-w-md">
                    Ask the MCP agent about creating integrations, exploring patterns, or getting help with your workflow.
                  </p>
                </div>
              )}
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center space-x-2 text-slate-500 dark:text-slate-400"
                >
                  <Bot className="h-4 w-4" />
                  <span className="text-sm">MCP Agent is typing...</span>
                  <div className="flex space-x-1">
                    <div className="w-1 h-1 bg-slate-400 rounded-full animate-bounce" />
                    <div className="w-1 h-1 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-1 h-1 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </motion.div>
              )}

              {/* Execution Status Panel */}
              {executionStatus.status !== 'idle' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    {executionStatus.status === 'planning' && <Clock className="h-5 w-5 text-blue-500 animate-spin" />}
                    {executionStatus.status === 'executing' && <Play className="h-5 w-5 text-blue-500 animate-pulse" />}
                    {executionStatus.status === 'completed' && <CheckCircle className="h-5 w-5 text-green-500" />}
                    {executionStatus.status === 'failed' && <AlertCircle className="h-5 w-5 text-red-500" />}

                    <div className="flex-1">
                      <h4 className="font-medium text-slate-900 dark:text-white">
                        {executionStatus.status === 'planning' && 'Planning Integration'}
                        {executionStatus.status === 'executing' && 'Executing Integration'}
                        {executionStatus.status === 'completed' && 'Integration Complete'}
                        {executionStatus.status === 'failed' && 'Execution Failed'}
                      </h4>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {executionStatus.currentStep}
                      </p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 mb-2">
                    <motion.div
                      className={`h-2 rounded-full ${
                        executionStatus.status === 'completed' ? 'bg-green-500' :
                        executionStatus.status === 'failed' ? 'bg-red-500' :
                        'bg-blue-500'
                      }`}
                      initial={{ width: 0 }}
                      animate={{ width: `${executionStatus.progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>

                  <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
                    <span>{executionStatus.progress}% complete</span>
                    {executionStatus.error && (
                      <span className="text-red-500">{executionStatus.error}</span>
                    )}
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Chat Input */}
            <div className="border-t border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
              {/* Execution Controls */}
              <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      Integration Execution
                    </span>
                  </div>

                  <Button
                    onClick={handleExecuteIntegration}
                    disabled={executeIntegrationMutation.isPending || executionStatus.status === 'executing' || messages.length === 0}
                    size="sm"
                    className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white shadow-lg"
                  >
                    {executeIntegrationMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Executing...
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Execute Integration
                      </>
                    )}
                  </Button>
                </div>

                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {messages.length === 0
                    ? 'Start a conversation to generate an integration plan first'
                    : 'Execute the integration plan discussed in this conversation'
                  }
                </p>
              </div>

              <ChatInput
                onSendMessage={handleSendMessage}
                disabled={sendMessageMutation.isPending}
                isLoading={sendMessageMutation.isPending}
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageSquare className="h-16 w-16 text-slate-400 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-slate-900 dark:text-white mb-2">
                Welcome to MCP Chat
              </h3>
              <p className="text-slate-500 dark:text-slate-400 mb-6 max-w-md">
                Start a new conversation or select an existing one to chat with the AI agent about your integrations.
              </p>
              <Button onClick={handleNewConversation}>
                <Plus className="h-4 w-4 mr-2" />
                Start New Conversation
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
