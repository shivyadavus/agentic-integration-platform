import { toast as sonnerToast } from 'sonner'

// Enhanced toast notifications with custom styling
export const toast = {
  success: (message: string, description?: string) => {
    sonnerToast.success(message, {
      description,
      style: {
        background: 'linear-gradient(135deg, #10b981, #059669)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '14px',
        fontWeight: '500',
      },
    })
  },
  
  error: (message: string, description?: string) => {
    sonnerToast.error(message, {
      description,
      style: {
        background: 'linear-gradient(135deg, #ef4444, #dc2626)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '14px',
        fontWeight: '500',
      },
    })
  },
  
  warning: (message: string, description?: string) => {
    sonnerToast.warning(message, {
      description,
      style: {
        background: 'linear-gradient(135deg, #f59e0b, #d97706)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '14px',
        fontWeight: '500',
      },
    })
  },
  
  info: (message: string, description?: string) => {
    sonnerToast.info(message, {
      description,
      style: {
        background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '14px',
        fontWeight: '500',
      },
    })
  },
  
  loading: (message: string, description?: string) => {
    return sonnerToast.loading(message, {
      description,
      style: {
        background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '14px',
        fontWeight: '500',
      },
    })
  },
  
  custom: (message: string, options?: any) => {
    sonnerToast(message, {
      ...options,
      style: {
        background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '14px',
        fontWeight: '500',
        ...options?.style,
      },
    })
  }
}

export { sonnerToast }