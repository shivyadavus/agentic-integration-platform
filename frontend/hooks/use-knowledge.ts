import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

// Hook for searching patterns
export function useSearchPatterns() {
  return useMutation({
    mutationFn: (data: { 
      description: string; 
      source_system_type?: string; 
      target_system_type?: string; 
      limit?: number 
    }) => api.knowledge.searchPatterns(data),
    onError: (error: any) => {
      toast.error(`Failed to search patterns: ${error.message}`);
    },
  });
}

// Hook for getting a specific pattern
export function usePattern(patternId: string) {
  return useQuery({
    queryKey: ['pattern', patternId],
    queryFn: () => api.knowledge.getPattern(patternId),
    enabled: !!patternId,
  });
}

// Hook for querying schemas
export function useQuerySchemas() {
  return useMutation({
    mutationFn: (data: { 
      system_type?: string; 
      schema_name?: string; 
      limit?: number 
    }) => api.knowledge.querySchemas(data),
    onError: (error: any) => {
      toast.error(`Failed to query schemas: ${error.message}`);
    },
  });
}

// Hook for semantic search
export function useSemanticSearch() {
  return useMutation({
    mutationFn: (data: { 
      query: string; 
      limit?: number; 
      min_similarity_score?: number; 
      filters?: any 
    }) => api.knowledge.semanticSearch(data),
    onError: (error: any) => {
      toast.error(`Failed to perform semantic search: ${error.message}`);
    },
  });
}

// Hook for getting knowledge stats
export function useKnowledgeStats() {
  return useQuery({
    queryKey: ['knowledge-stats'],
    queryFn: () => api.knowledge.getStats(),
    staleTime: 60000, // 1 minute
  });
}
