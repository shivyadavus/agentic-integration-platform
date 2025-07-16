import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

// Hook for starting a new MCP conversation
export function useStartConversation() {
  return useMutation({
    mutationFn: (data: { initial_request: string; user_id?: string }) => 
      api.mcp.startConversation(data),
    onSuccess: () => {
      toast.success('Conversation started successfully!');
    },
    onError: (error: any) => {
      toast.error(`Failed to start conversation: ${error.message}`);
    },
  });
}

// Hook for sending a message in a conversation
export function useSendMessage() {
  return useMutation({
    mutationFn: ({ conversationId, message }: { conversationId: string; message: string }) => 
      api.mcp.sendMessage(conversationId, { message }),
    onError: (error: any) => {
      toast.error(`Failed to send message: ${error.message}`);
    },
  });
}

// Hook for getting conversation details
export function useConversation(conversationId: string) {
  return useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => api.mcp.getConversation(conversationId),
    enabled: !!conversationId,
  });
}

// Hook for retrieving context
export function useRetrieveContext() {
  return useMutation({
    mutationFn: ({ conversationId, data }: { 
      conversationId: string; 
      data: { 
        source_system_type?: string; 
        target_system_type?: string; 
        search_patterns?: boolean 
      } 
    }) => api.mcp.retrieveContext(conversationId, data),
    onError: (error: any) => {
      toast.error(`Failed to retrieve context: ${error.message}`);
    },
  });
}

// Hook for generating integration plan from conversation
export function useGeneratePlanFromConversation() {
  return useMutation({
    mutationFn: ({ conversationId, data }: { 
      conversationId: string; 
      data: { 
        include_testing?: boolean; 
        include_deployment?: boolean; 
        detail_level?: string 
      } 
    }) => api.mcp.generatePlan(conversationId, data),
    onSuccess: () => {
      toast.success('Integration plan generated successfully!');
    },
    onError: (error: any) => {
      toast.error(`Failed to generate plan: ${error.message}`);
    },
  });
}

// Hook for approving integration
export function useApproveIntegration() {
  return useMutation({
    mutationFn: ({ conversationId, data }: { 
      conversationId: string; 
      data: { 
        approved: boolean; 
        notes?: string; 
        modifications_requested?: string[] 
      } 
    }) => api.mcp.approveIntegration(conversationId, data),
    onSuccess: () => {
      toast.success('Integration approval processed successfully!');
    },
    onError: (error: any) => {
      toast.error(`Failed to process approval: ${error.message}`);
    },
  });
}
