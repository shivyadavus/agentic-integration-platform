'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { useCreateIntegration, useGenerateIntegrationPlan, useDeployIntegration } from '@/hooks/use-integrations'
import {
  ArrowRight,
  ArrowLeft,
  Check,
  Zap,
  Settings,
  Code,
  Rocket,
  MessageSquare,
  Loader2
} from 'lucide-react'

interface IntegrationWizardProps {
  onComplete: () => void
}

type Step = 'describe' | 'configure' | 'generate' | 'deploy'

export function IntegrationWizard({ onComplete }: IntegrationWizardProps) {
  const [currentStep, setCurrentStep] = useState<Step>('describe')
  const [integrationId, setIntegrationId] = useState<string | null>(null)

  // API hooks
  const createIntegration = useCreateIntegration()
  const generatePlan = useGenerateIntegrationPlan()
  const deployIntegration = useDeployIntegration()

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    sourceSystem: '',
    targetSystem: '',
    integrationType: 'sync'
  })

  const steps = [
    {
      id: 'describe' as const,
      title: 'Describe Integration',
      description: 'Tell us what you want to integrate',
      icon: MessageSquare,
      color: 'blue'
    },
    {
      id: 'configure' as const,
      title: 'Configure Settings',
      description: 'Set up integration parameters',
      icon: Settings,
      color: 'purple'
    },
    {
      id: 'generate' as const,
      title: 'Generate Code',
      description: 'AI creates your integration',
      icon: Code,
      color: 'green'
    },
    {
      id: 'deploy' as const,
      title: 'Deploy & Test',
      description: 'Launch your integration',
      icon: Rocket,
      color: 'orange'
    }
  ]

  const currentStepIndex = steps.findIndex(step => step.id === currentStep)
  const isLastStep = currentStepIndex === steps.length - 1
  const isFirstStep = currentStepIndex === 0

  const handleNext = async () => {
    if (currentStep === 'describe' && !integrationId) {
      // Validate required fields
      if (!formData.name.trim()) {
        alert('Please enter an integration name');
        return;
      }
      if (!formData.description.trim()) {
        alert('Please enter a description');
        return;
      }

      // Create integration when moving from describe step
      try {
        const result = await createIntegration.mutateAsync({
          name: formData.name.trim(),
          natural_language_spec: formData.description.trim(),
          integration_type: formData.integrationType as any,
          status: 'draft'
        });
        setIntegrationId(result.id);
      } catch (error) {
        console.error('Failed to create integration:', error);
        alert('Failed to create integration. Please try again.');
        return;
      }
    }

    if (isLastStep) {
      onComplete()
    } else {
      const nextStep = steps[currentStepIndex + 1]
      if (nextStep) {
        setCurrentStep(nextStep.id)
      }
    }
  }

  const handlePrevious = () => {
    if (!isFirstStep) {
      const prevStep = steps[currentStepIndex - 1]
      if (prevStep) {
        setCurrentStep(prevStep.id)
      }
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 'describe':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Integration Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Salesforce to Billing System"
                className="w-full px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Natural Language Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe what you want this integration to do in plain English..."
                rows={4}
                className="w-full px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Source System
                </label>
                <select
                  value={formData.sourceSystem}
                  onChange={(e) => setFormData({ ...formData, sourceSystem: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                >
                  <option value="">Select source...</option>
                  <option value="salesforce">Salesforce</option>
                  <option value="hubspot">HubSpot</option>
                  <option value="stripe">Stripe</option>
                  <option value="shopify">Shopify</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Target System
                </label>
                <select
                  value={formData.targetSystem}
                  onChange={(e) => setFormData({ ...formData, targetSystem: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                >
                  <option value="">Select target...</option>
                  <option value="quickbooks">QuickBooks</option>
                  <option value="xero">Xero</option>
                  <option value="netsuite">NetSuite</option>
                  <option value="custom">Custom API</option>
                </select>
              </div>
            </div>
          </div>
        )
      
      case 'configure':
        return (
          <div className="space-y-6">
            <div className="text-center py-12">
              <Settings className="h-16 w-16 text-slate-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                Configuration Step
              </h3>
              <p className="text-slate-500 dark:text-slate-400">
                Advanced configuration options will be available here
              </p>
            </div>
          </div>
        )
      
      case 'generate':
        return (
          <div className="space-y-6">
            <div className="text-center py-12">
              <div className="relative">
                <Code className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="absolute -top-2 -right-2"
                >
                  <Zap className="h-6 w-6 text-yellow-500" />
                </motion.div>
              </div>
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                AI Code Generation
              </h3>
              <p className="text-slate-500 dark:text-slate-400">
                Our AI is generating your integration code based on your requirements
              </p>
            </div>
          </div>
        )
      
      case 'deploy':
        return (
          <div className="space-y-6">
            <div className="text-center py-12">
              <Rocket className="h-16 w-16 text-slate-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                Ready to Deploy
              </h3>
              <p className="text-slate-500 dark:text-slate-400">
                Your integration is ready to be deployed and tested
              </p>
            </div>
          </div>
        )
      
      default:
        return null
    }
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Progress Header */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            {steps.map((step, index) => {
              const isActive = step.id === currentStep
              const isCompleted = index < currentStepIndex
              const Icon = step.icon
              
              return (
                <div key={step.id} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    isCompleted
                      ? 'bg-green-500 border-green-500 text-white'
                      : isActive
                      ? 'bg-blue-500 border-blue-500 text-white'
                      : 'bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600 text-slate-400'
                  }`}>
                    {isCompleted ? (
                      <Check className="h-5 w-5" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  
                  {index < steps.length - 1 && (
                    <div className={`w-20 h-0.5 mx-4 ${
                      isCompleted ? 'bg-green-500' : 'bg-slate-200 dark:bg-slate-700'
                    }`} />
                  )}
                </div>
              )
            })}
          </div>
          
          <div className="text-center">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
              {steps[currentStepIndex]?.title || 'Loading...'}
            </h2>
            <p className="text-slate-600 dark:text-slate-400">
              {steps[currentStepIndex]?.description || 'Please wait...'}
            </p>
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-8"
          >
            {renderStepContent()}
          </motion.div>
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-700 p-6">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={isFirstStep}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>
          
          <div className="text-sm text-slate-500 dark:text-slate-400">
            Step {currentStepIndex + 1} of {steps.length}
          </div>
          
          <Button
            onClick={handleNext}
            disabled={createIntegration.isPending || generatePlan.isPending || deployIntegration.isPending}
          >
            {createIntegration.isPending || generatePlan.isPending || deployIntegration.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                {isLastStep ? 'Complete' : 'Next'}
                {!isLastStep && <ArrowRight className="h-4 w-4 ml-2" />}
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
