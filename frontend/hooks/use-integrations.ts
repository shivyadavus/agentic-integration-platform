import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import { addSuccessNotification, addErrorNotification } from './use-notifications';

// Hook for listing integrations
export function useIntegrations(params?: { skip?: number; limit?: number; status_filter?: string }) {
  return useQuery({
    queryKey: ['integrations', params],
    queryFn: () => api.integrations.list(params),
    staleTime: 30000, // 30 seconds
  });
}

// Hook for getting a specific integration
export function useIntegration(id: string) {
  return useQuery({
    queryKey: ['integrations', id],
    queryFn: () => api.integrations.get(id),
    enabled: !!id,
  });
}

// Hook for creating an integration
export function useCreateIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; natural_language_spec: string; integration_type?: string; status?: string }) => 
      api.integrations.create(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      toast.success('Integration created successfully!');
      addSuccessNotification(
        'Integration Created',
        `${data.name} has been created successfully`
      );
    },
    onError: (error: any) => {
      toast.error(`Failed to create integration: ${error.message}`);
      addErrorNotification(
        'Integration Creation Failed',
        error.message || 'Failed to create integration'
      );
    },
  });
}

// Hook for generating integration plan
export function useGenerateIntegrationPlan() {
  return useMutation({
    mutationFn: ({ id, data }: { 
      id: string; 
      data: { 
        source_system_type: string; 
        target_system_type: string; 
        estimated_complexity?: string; 
        additional_requirements?: string 
      } 
    }) => api.integrations.generatePlan(id, data),
    onSuccess: (data) => {
      toast.success('Integration plan generated successfully!');
      addSuccessNotification(
        'Integration Plan Generated',
        'Your integration plan is ready for review'
      );
    },
    onError: (error: any) => {
      toast.error(`Failed to generate plan: ${error.message}`);
      addErrorNotification(
        'Plan Generation Failed',
        error.message || 'Failed to generate integration plan'
      );
    },
  });
}

// Hook for deploying integration
export function useDeployIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { 
      id: string; 
      data: { 
        environment?: string; 
        configuration?: any; 
        auto_approve?: boolean 
      } 
    }) => api.integrations.deploy(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      toast.success('Integration deployed successfully!');
      addSuccessNotification(
        'Integration Deployed',
        `Integration is now live at ${data.deployment_url || 'production'}`
      );
    },
    onError: (error: any) => {
      toast.error(`Failed to deploy integration: ${error.message}`);
      addErrorNotification(
        'Deployment Failed',
        error.message || 'Failed to deploy integration'
      );
    },
  });
}
