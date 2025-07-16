'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { useIntegrations } from '@/hooks/use-integrations'
import { useSemanticSearch } from '@/hooks/use-knowledge'
import { 
  Search, 
  X, 
  Clock, 
  Zap,
  FileText,
  Database,
  ArrowRight,
  Loader2
} from 'lucide-react'

interface SearchModalProps {
  isOpen: boolean
  onClose: () => void
}

export function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('')
  const [activeTab, setActiveTab] = useState<'integrations' | 'knowledge'>('integrations')
  
  const { data: integrations } = useIntegrations()
  const semanticSearch = useSemanticSearch()

  // Filter integrations based on query
  const filteredIntegrations = integrations?.filter(integration =>
    integration.name.toLowerCase().includes(query.toLowerCase()) ||
    integration.natural_language_spec.toLowerCase().includes(query.toLowerCase())
  ) || []

  // Perform semantic search when query changes and knowledge tab is active
  useEffect(() => {
    if (query.length > 2 && activeTab === 'knowledge') {
      semanticSearch.mutate({ query, limit: 5 })
    }
  }, [query, activeTab])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose()
    }
  }

  // Global keyboard shortcut
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        if (!isOpen) {
          // This would need to be handled by parent component
        }
      }
    }

    document.addEventListener('keydown', handleGlobalKeyDown)
    return () => document.removeEventListener('keydown', handleGlobalKeyDown)
  }, [isOpen])

  const recentSearches = [
    'Salesforce integration',
    'API rate limits',
    'Webhook configuration',
    'Data mapping'
  ]

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          
          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.2 }}
            className="fixed top-20 left-1/2 transform -translate-x-1/2 w-full max-w-2xl bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 z-50 overflow-hidden"
          >
            {/* Search Input */}
            <div className="p-4 border-b border-slate-200 dark:border-slate-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Search integrations, patterns, or ask a question..."
                  className="w-full pl-10 pr-10 py-3 bg-transparent border-none outline-none text-slate-900 dark:text-white placeholder-slate-500 text-lg"
                  autoFocus
                />
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-200 dark:border-slate-700">
              <button
                onClick={() => setActiveTab('integrations')}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'integrations'
                    ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <FileText className="h-4 w-4 inline mr-2" />
                Integrations
              </button>
              <button
                onClick={() => setActiveTab('knowledge')}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'knowledge'
                    ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Database className="h-4 w-4 inline mr-2" />
                Knowledge
              </button>
            </div>

            {/* Results */}
            <div className="max-h-96 overflow-y-auto">
              {query.length === 0 ? (
                <div className="p-6">
                  <h3 className="text-sm font-medium text-slate-900 dark:text-white mb-3">
                    Recent searches
                  </h3>
                  <div className="space-y-2">
                    {recentSearches.map((search, index) => (
                      <button
                        key={index}
                        onClick={() => setQuery(search)}
                        className="flex items-center w-full p-2 text-left text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors"
                      >
                        <Clock className="h-4 w-4 mr-3" />
                        {search}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-4">
                  {activeTab === 'integrations' ? (
                    <div className="space-y-2">
                      {filteredIntegrations.length === 0 ? (
                        <div className="text-center py-8 text-slate-500 dark:text-slate-400">
                          No integrations found for "{query}"
                        </div>
                      ) : (
                        filteredIntegrations.map((integration) => (
                          <motion.div
                            key={integration.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-3 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg cursor-pointer group"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <h4 className="font-medium text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
                                  {integration.name}
                                </h4>
                                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                                  {integration.natural_language_spec}
                                </p>
                                <div className="flex items-center mt-2 space-x-2">
                                  <span className={`px-2 py-1 text-xs rounded-full ${
                                    integration.status === 'active' 
                                      ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                                      : integration.status === 'draft'
                                      ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400'
                                      : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400'
                                  }`}>
                                    {integration.status}
                                  </span>
                                  <span className="text-xs text-slate-500 dark:text-slate-400">
                                    {integration.integration_type}
                                  </span>
                                </div>
                              </div>
                              <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400" />
                            </div>
                          </motion.div>
                        ))
                      )}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {semanticSearch.isPending ? (
                        <div className="flex items-center justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                          <span className="ml-2 text-slate-600 dark:text-slate-400">
                            Searching knowledge base...
                          </span>
                        </div>
                      ) : semanticSearch.data?.results?.length === 0 ? (
                        <div className="text-center py-8 text-slate-500 dark:text-slate-400">
                          No knowledge found for "{query}"
                        </div>
                      ) : (
                        semanticSearch.data?.results?.map((result: any, index: number) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-3 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg cursor-pointer group"
                          >
                            <div className="flex items-start space-x-3">
                              <Zap className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-1 flex-shrink-0" />
                              <div className="flex-1">
                                <h4 className="font-medium text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
                                  {result.title || 'Knowledge Result'}
                                </h4>
                                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                                  {result.content || result.description || 'Relevant knowledge found'}
                                </p>
                                {result.score && (
                                  <div className="mt-2">
                                    <span className="text-xs text-slate-500 dark:text-slate-400">
                                      Relevance: {Math.round(result.score * 100)}%
                                    </span>
                                  </div>
                                )}
                              </div>
                            </div>
                          </motion.div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>Press ESC to close</span>
                <span>
                  {activeTab === 'integrations' 
                    ? `${filteredIntegrations.length} results`
                    : semanticSearch.data?.results?.length 
                      ? `${semanticSearch.data.results.length} results`
                      : ''
                  }
                </span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
