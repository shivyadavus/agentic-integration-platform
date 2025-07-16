'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { 
  Search, 
  Filter, 
  Maximize2, 
  Download, 
  RefreshCw,
  Network,
  Zap,
  Database,
  GitBranch
} from 'lucide-react'

interface Entity {
  id: string
  name: string
  entity_type: string
  description?: string
  properties: Record<string, any>
}

interface Relationship {
  id: string
  source_entity_id: string
  target_entity_id: string
  relationship_type: string
  confidence_score: number
}

export function KnowledgeGraph() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null)
  const [filter, setFilter] = useState('all')
  const svgRef = useRef<SVGSVGElement>(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })

  // Fetch entities
  const { data: entities, isLoading: entitiesLoading, error: entitiesError } = useQuery({
    queryKey: ['knowledge-entities'],
    queryFn: async (): Promise<Entity[]> => {
      console.log('Fetching knowledge entities from API...');
      const response = await fetch('http://localhost:8000/api/v1/knowledge/entities')
      if (!response.ok) throw new Error('Failed to fetch entities')
      const data = await response.json()
      console.log('Knowledge entities fetched:', data);

      // Transform the API response to match our interface
      const transformed = Array.isArray(data) ? data.map(item => ({
        id: item.id,
        name: item.properties.name || 'Unnamed Entity',
        entity_type: item.entity_type,
        description: item.properties.description || '',
        properties: item.properties
      })) : []

      console.log('Transformed entities:', transformed);
      return transformed;
    }
  })

  // Fetch relationships
  const { data: relationships } = useQuery({
    queryKey: ['knowledge-relationships'],
    queryFn: async (): Promise<Relationship[]> => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/knowledge/relationships')
        if (!response.ok) throw new Error('Failed to fetch relationships')
        const data = await response.json()
        return Array.isArray(data) ? data : []
      } catch (error) {
        console.warn('Knowledge relationships not available:', error)
        return []
      }
    }
  })

  // Search entities
  const { data: searchResults } = useQuery({
    queryKey: ['knowledge-search', searchQuery],
    queryFn: async (): Promise<Entity[]> => {
      if (!searchQuery.trim()) return []
      const response = await fetch(`http://localhost:8000/api/v1/knowledge/semantic/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, limit: 10 })
      })
      if (!response.ok) throw new Error('Failed to search entities')
      return response.json()
    },
    enabled: searchQuery.length > 2
  })

  const getEntityTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'system':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
      case 'api_endpoint':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
      case 'pattern':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300'
      case 'business_object':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-300'
      case 'integration':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300'
    }
  }

  const getEntityIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'system':
        return Database
      case 'api_endpoint':
        return Zap
      case 'pattern':
        return GitBranch
      case 'business_object':
        return Network
      case 'integration':
        return Network
      default:
        return Network
    }
  }

  const filteredEntities = entities?.filter(entity => {
    if (filter === 'all') return true
    return entity.entity_type === filter
  }) || []

  const displayEntities = searchQuery.length > 2 ? (searchResults || []) : filteredEntities

  // Create sample relationships based on entity names and types
  const createSampleRelationships = (entities: Entity[]) => {
    const relationships = []

    // Find entities by name patterns
    const salesforce = entities.find(e => e.properties?.name?.includes('Salesforce'))
    const quickbooks = entities.find(e => e.properties?.name?.includes('QuickBooks'))
    const stripe = entities.find(e => e.properties?.name?.includes('Stripe'))
    const hubspot = entities.find(e => e.properties?.name?.includes('HubSpot'))

    const salesforceApi = entities.find(e => e.properties?.name?.includes('Salesforce') && e.entity_type === 'api_endpoint')
    const quickbooksApi = entities.find(e => e.properties?.name?.includes('QuickBooks') && e.entity_type === 'api_endpoint')
    const stripeApi = entities.find(e => e.properties?.name?.includes('Stripe') && e.entity_type === 'api_endpoint')
    const hubspotApi = entities.find(e => e.properties?.name?.includes('HubSpot') && e.entity_type === 'api_endpoint')

    const customerSync = entities.find(e => e.properties?.name?.includes('Customer') && e.entity_type === 'pattern')
    const orderCash = entities.find(e => e.properties?.name?.includes('Order-to-Cash'))
    const leadNurturing = entities.find(e => e.properties?.name?.includes('Lead Nurturing'))

    const customer = entities.find(e => e.properties?.name === 'Customer' && e.entity_type === 'business_object')
    const invoice = entities.find(e => e.properties?.name === 'Invoice')
    const product = entities.find(e => e.properties?.name === 'Product')

    // System to API relationships
    if (salesforce && salesforceApi) relationships.push({ source: salesforce.id, target: salesforceApi.id, type: 'HAS_API', confidence: 0.95 })
    if (quickbooks && quickbooksApi) relationships.push({ source: quickbooks.id, target: quickbooksApi.id, type: 'HAS_API', confidence: 0.95 })
    if (stripe && stripeApi) relationships.push({ source: stripe.id, target: stripeApi.id, type: 'HAS_API', confidence: 0.95 })
    if (hubspot && hubspotApi) relationships.push({ source: hubspot.id, target: hubspotApi.id, type: 'HAS_API', confidence: 0.95 })

    // Pattern to System relationships
    if (customerSync && salesforce) relationships.push({ source: customerSync.id, target: salesforce.id, type: 'APPLIES_TO', confidence: 0.9 })
    if (customerSync && quickbooks) relationships.push({ source: customerSync.id, target: quickbooks.id, type: 'APPLIES_TO', confidence: 0.9 })
    if (customerSync && hubspot) relationships.push({ source: customerSync.id, target: hubspot.id, type: 'APPLIES_TO', confidence: 0.8 })

    if (orderCash && salesforce) relationships.push({ source: orderCash.id, target: salesforce.id, type: 'APPLIES_TO', confidence: 0.9 })
    if (orderCash && stripe) relationships.push({ source: orderCash.id, target: stripe.id, type: 'APPLIES_TO', confidence: 0.9 })
    if (orderCash && quickbooks) relationships.push({ source: orderCash.id, target: quickbooks.id, type: 'APPLIES_TO', confidence: 0.9 })

    if (leadNurturing && hubspot) relationships.push({ source: leadNurturing.id, target: hubspot.id, type: 'APPLIES_TO', confidence: 0.95 })
    if (leadNurturing && salesforce) relationships.push({ source: leadNurturing.id, target: salesforce.id, type: 'APPLIES_TO', confidence: 0.7 })

    // Business Object to System relationships
    if (customer && salesforce) relationships.push({ source: customer.id, target: salesforce.id, type: 'STORED_IN', confidence: 0.9 })
    if (customer && quickbooks) relationships.push({ source: customer.id, target: quickbooks.id, type: 'STORED_IN', confidence: 0.8 })
    if (customer && stripe) relationships.push({ source: customer.id, target: stripe.id, type: 'STORED_IN', confidence: 0.8 })
    if (customer && hubspot) relationships.push({ source: customer.id, target: hubspot.id, type: 'STORED_IN', confidence: 0.7 })

    if (invoice && quickbooks) relationships.push({ source: invoice.id, target: quickbooks.id, type: 'STORED_IN', confidence: 0.95 })
    if (invoice && stripe) relationships.push({ source: invoice.id, target: stripe.id, type: 'STORED_IN', confidence: 0.8 })
    if (invoice && salesforce) relationships.push({ source: invoice.id, target: salesforce.id, type: 'STORED_IN', confidence: 0.6 })

    if (product && salesforce) relationships.push({ source: product.id, target: salesforce.id, type: 'STORED_IN', confidence: 0.9 })
    if (product && quickbooks) relationships.push({ source: product.id, target: quickbooks.id, type: 'STORED_IN', confidence: 0.8 })
    if (product && stripe) relationships.push({ source: product.id, target: stripe.id, type: 'STORED_IN', confidence: 0.6 })

    // Pattern interdependencies
    if (customerSync && orderCash) relationships.push({ source: customerSync.id, target: orderCash.id, type: 'ENABLES', confidence: 0.8 })
    if (leadNurturing && customerSync) relationships.push({ source: leadNurturing.id, target: customerSync.id, type: 'FEEDS_INTO', confidence: 0.7 })

    return relationships
  }

  // Create graph data for visualization
  const graphData = {
    nodes: displayEntities.map(entity => ({
      id: entity.id,
      name: entity.properties?.name || entity.name,
      type: entity.entity_type,
      description: entity.description,
      properties: entity.properties
    })),
    links: createSampleRelationships(displayEntities)
  }

  // Update dimensions on window resize
  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current) {
        const container = svgRef.current.parentElement
        if (container) {
          setDimensions({
            width: container.clientWidth,
            height: container.clientHeight
          })
        }
      }
    }

    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  // Simple force-directed layout simulation
  useEffect(() => {
    if (!svgRef.current || !graphData.nodes.length) return

    const svg = svgRef.current
    const { width, height } = dimensions

    // Clear previous content
    svg.innerHTML = ''

    // Create SVG groups
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    svg.appendChild(g)

    // Simple circular layout for now
    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) / 3

    // Position nodes in a circle
    const nodePositions = graphData.nodes.map((node, index) => {
      const angle = (index / graphData.nodes.length) * 2 * Math.PI
      return {
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      }
    })

    // Draw links first (so they appear behind nodes)
    graphData.links.forEach(link => {
      const sourceNode = nodePositions.find(n => n.id === link.source)
      const targetNode = nodePositions.find(n => n.id === link.target)

      if (sourceNode && targetNode) {
        // Draw line
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
        line.setAttribute('x1', sourceNode.x.toString())
        line.setAttribute('y1', sourceNode.y.toString())
        line.setAttribute('x2', targetNode.x.toString())
        line.setAttribute('y2', targetNode.y.toString())

        // Color based on relationship type
        const linkColors = {
          'HAS_API': '#3b82f6',
          'APPLIES_TO': '#8b5cf6',
          'STORED_IN': '#10b981',
          'ENABLES': '#f59e0b',
          'FEEDS_INTO': '#ef4444'
        }
        line.setAttribute('stroke', linkColors[link.type as keyof typeof linkColors] || '#e2e8f0')
        line.setAttribute('stroke-width', Math.max(1, (link.confidence * 3)).toString())
        line.setAttribute('opacity', (0.4 + link.confidence * 0.4).toString())
        g.appendChild(line)

        // Add relationship label
        const midX = (sourceNode.x + targetNode.x) / 2
        const midY = (sourceNode.y + targetNode.y) / 2

        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text')
        label.setAttribute('x', midX.toString())
        label.setAttribute('y', midY.toString())
        label.setAttribute('text-anchor', 'middle')
        label.setAttribute('font-size', '10')
        label.setAttribute('font-weight', '500')
        label.setAttribute('fill', '#6b7280')
        label.setAttribute('opacity', '0.8')
        label.textContent = link.type

        // Add background for better readability
        const bbox = label.getBBox?.() || { x: midX - 20, y: midY - 5, width: 40, height: 10 }
        const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
        bg.setAttribute('x', (bbox.x - 2).toString())
        bg.setAttribute('y', (bbox.y - 1).toString())
        bg.setAttribute('width', (bbox.width + 4).toString())
        bg.setAttribute('height', (bbox.height + 2).toString())
        bg.setAttribute('fill', 'white')
        bg.setAttribute('opacity', '0.8')
        bg.setAttribute('rx', '2')

        g.appendChild(bg)
        g.appendChild(label)
      }
    })

    // Draw nodes
    nodePositions.forEach(node => {
      // Node circle
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
      circle.setAttribute('cx', node.x.toString())
      circle.setAttribute('cy', node.y.toString())
      circle.setAttribute('r', '20')

      // Color based on type
      const colors = {
        system: '#3b82f6',
        api_endpoint: '#10b981',
        pattern: '#8b5cf6',
        business_object: '#f59e0b'
      }
      circle.setAttribute('fill', colors[node.type as keyof typeof colors] || '#6b7280')
      circle.setAttribute('stroke', '#ffffff')
      circle.setAttribute('stroke-width', '2')
      circle.setAttribute('cursor', 'pointer')

      // Add hover effects
      circle.addEventListener('mouseenter', () => {
        circle.setAttribute('r', '25')
        circle.setAttribute('opacity', '0.8')
      })
      circle.addEventListener('mouseleave', () => {
        circle.setAttribute('r', '20')
        circle.setAttribute('opacity', '1')
      })

      // Add click handler
      circle.addEventListener('click', () => {
        const entity = entities?.find(e => e.id === node.id)
        if (entity) setSelectedEntity(entity)
      })

      g.appendChild(circle)

      // Node label
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
      text.setAttribute('x', node.x.toString())
      text.setAttribute('y', (node.y + 35).toString())
      text.setAttribute('text-anchor', 'middle')
      text.setAttribute('font-size', '12')
      text.setAttribute('font-weight', '500')
      text.setAttribute('fill', '#374151')
      text.textContent = node.name.length > 15 ? node.name.substring(0, 15) + '...' : node.name
      g.appendChild(text)
    })

  }, [graphData, dimensions, entities])

  return (
    <div className="h-full flex bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Sidebar */}
      <div className="w-80 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-r border-slate-200 dark:border-slate-700 flex flex-col">
        {/* Search Header */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search knowledge graph..."
              className="w-full pl-10 pr-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-slate-500" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="text-sm border border-slate-200 dark:border-slate-700 rounded-md px-2 py-1 bg-white dark:bg-slate-800"
            >
              <option value="all">All Types</option>
              <option value="system">Systems</option>
              <option value="api_endpoint">API Endpoints</option>
              <option value="pattern">Patterns</option>
              <option value="business_object">Business Objects</option>
            </select>
          </div>
        </div>

        {/* Entity List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {entitiesLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse"
                />
              ))}
            </div>
          ) : displayEntities.length === 0 ? (
            <div className="text-center py-8">
              <Network className="h-12 w-12 text-slate-400 mx-auto mb-3" />
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {searchQuery ? 'No entities found' : 'No entities available'}
              </p>
            </div>
          ) : (
            displayEntities.map((entity, index) => {
              const Icon = getEntityIcon(entity.entity_type)
              const isSelected = selectedEntity?.id === entity.id
              
              return (
                <motion.div
                  key={entity.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                    isSelected
                      ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
                      : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
                  }`}
                  onClick={() => setSelectedEntity(entity)}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${getEntityTypeColor(entity.entity_type)}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-slate-900 dark:text-white text-sm truncate">
                        {entity.name}
                      </h3>
                      <p className="text-xs text-slate-500 dark:text-slate-400 capitalize">
                        {entity.entity_type}
                      </p>
                      {entity.description && (
                        <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 line-clamp-2">
                          {entity.description}
                        </p>
                      )}
                    </div>
                  </div>
                </motion.div>
              )
            })
          )}
        </div>
      </div>

      {/* Main Graph Area */}
      <div className="flex-1 flex flex-col">
        {/* Graph Header */}
        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                Knowledge Graph Visualization
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Explore integration patterns and relationships
              </p>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Maximize2 className="h-4 w-4 mr-2" />
                Fullscreen
              </Button>
            </div>
          </div>
        </div>

        {/* Graph Visualization */}
        <div className="flex-1 relative overflow-hidden bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-800 dark:to-slate-900">
          {displayEntities.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Network className="h-24 w-24 text-slate-300 dark:text-slate-600 mx-auto mb-6" />
                <h3 className="text-xl font-medium text-slate-900 dark:text-white mb-2">
                  {entitiesLoading ? 'Loading Knowledge Graph...' : 'No Entities Found'}
                </h3>
                <p className="text-slate-500 dark:text-slate-400 max-w-md">
                  {entitiesLoading
                    ? 'Please wait while we load the knowledge graph data.'
                    : searchQuery
                      ? 'Try adjusting your search query or filters.'
                      : 'No entities are available in the knowledge graph yet.'
                  }
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* Graph Legend */}
              <div className="absolute top-4 left-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-lg p-3 shadow-lg border border-slate-200 dark:border-slate-700">
                <h4 className="text-sm font-medium text-slate-900 dark:text-white mb-2">Entity Types</h4>
                <div className="space-y-1 text-xs mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span className="text-slate-600 dark:text-slate-300">Systems</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-slate-600 dark:text-slate-300">API Endpoints</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                    <span className="text-slate-600 dark:text-slate-300">Patterns</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                    <span className="text-slate-600 dark:text-slate-300">Business Objects</span>
                  </div>
                </div>

                <h4 className="text-sm font-medium text-slate-900 dark:text-white mb-2">Relationships</h4>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-0.5 bg-blue-500"></div>
                    <span className="text-slate-600 dark:text-slate-300">HAS_API</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-0.5 bg-purple-500"></div>
                    <span className="text-slate-600 dark:text-slate-300">APPLIES_TO</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-0.5 bg-green-500"></div>
                    <span className="text-slate-600 dark:text-slate-300">STORED_IN</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-0.5 bg-amber-500"></div>
                    <span className="text-slate-600 dark:text-slate-300">ENABLES</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-0.5 bg-red-500"></div>
                    <span className="text-slate-600 dark:text-slate-300">FEEDS_INTO</span>
                  </div>
                </div>
              </div>

              {/* Graph Stats */}
              <div className="absolute top-4 right-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-lg p-3 shadow-lg border border-slate-200 dark:border-slate-700">
                <div className="text-xs text-slate-600 dark:text-slate-300 space-y-1">
                  <div>Nodes: {graphData.nodes.length}</div>
                  <div>Links: {graphData.links.length}</div>
                </div>
              </div>

              {/* Interactive Instructions */}
              <div className="absolute bottom-4 left-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-lg p-3 shadow-lg border border-slate-200 dark:border-slate-700">
                <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1">
                  <div>• Click nodes to view details</div>
                  <div>• Hover for interactions</div>
                  <div>• Use filters to focus</div>
                </div>
              </div>
            </>
          )}

          {/* SVG Graph */}
          <svg
            ref={svgRef}
            className="w-full h-full"
            style={{ background: 'transparent' }}
          />
        </div>

        {/* Entity Details Panel */}
        {selectedEntity && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-700 p-4"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-3">
                  <div className={`p-2 rounded-lg ${getEntityTypeColor(selectedEntity.entity_type)}`}>
                    {(() => {
                      const Icon = getEntityIcon(selectedEntity.entity_type)
                      return <Icon className="h-4 w-4" />
                    })()}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white">
                      {selectedEntity.name}
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400 capitalize">
                      {selectedEntity.entity_type}
                    </p>
                  </div>
                </div>
                
                {selectedEntity.description && (
                  <p className="text-sm text-slate-600 dark:text-slate-300 mb-3">
                    {selectedEntity.description}
                  </p>
                )}
                
                {Object.keys(selectedEntity.properties).length > 0 && (
                  <div className="space-y-1">
                    <h4 className="text-sm font-medium text-slate-900 dark:text-white">
                      Properties:
                    </h4>
                    <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1">
                      {Object.entries(selectedEntity.properties).map(([key, value]) => (
                        <div key={key} className="flex">
                          <span className="font-medium w-20">{key}:</span>
                          <span>{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedEntity(null)}
              >
                Close
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
