'use client'

import { Button } from '@/components/ui/button'
import { 
  Plus, 
  MessageSquare, 
  Network, 
  Download,
  Upload,
  Settings
} from 'lucide-react'

export function QuickActions() {
  const actions = [
    {
      label: 'New Integration',
      icon: Plus,
      variant: 'default' as const,
      onClick: () => console.log('Create integration')
    },
    {
      label: 'Chat with AI',
      icon: MessageSquare,
      variant: 'outline' as const,
      onClick: () => console.log('Open chat')
    },
    {
      label: 'Knowledge Graph',
      icon: Network,
      variant: 'outline' as const,
      onClick: () => console.log('Open knowledge graph')
    },
    {
      label: 'Import',
      icon: Upload,
      variant: 'outline' as const,
      onClick: () => console.log('Import integration')
    },
    {
      label: 'Export',
      icon: Download,
      variant: 'outline' as const,
      onClick: () => console.log('Export integrations')
    }
  ]

  return (
    <div className="flex items-center space-x-2">
      {actions.map((action) => {
        const Icon = action.icon
        
        return (
          <Button
            key={action.label}
            variant={action.variant}
            size="sm"
            onClick={action.onClick}
            className="flex items-center space-x-2"
          >
            <Icon className="h-4 w-4" />
            <span className="hidden sm:inline">{action.label}</span>
          </Button>
        )
      })}
    </div>
  )
}
