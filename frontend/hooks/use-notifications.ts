'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: string
  read: boolean
  actionUrl?: string
}

interface NotificationStore {
  notifications: Notification[]
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  removeNotification: (id: string) => void
  clearAll: () => void
  getUnreadCount: () => number
}

export const useNotifications = create<NotificationStore>()(
  persist(
    (set, get) => ({
      notifications: [
        {
          id: '1',
          type: 'success',
          title: 'Integration Deployed',
          message: 'Salesforce to QuickBooks integration is now live',
          timestamp: '2 minutes ago',
          read: false
        },
        {
          id: '2',
          type: 'warning',
          title: 'API Rate Limit',
          message: 'Approaching rate limit for Stripe integration',
          timestamp: '15 minutes ago',
          read: false
        },
        {
          id: '3',
          type: 'info',
          title: 'System Update',
          message: 'New MCP agent features available',
          timestamp: '1 hour ago',
          read: true
        }
      ],

      addNotification: (notification) => {
        const newNotification: Notification = {
          ...notification,
          id: Date.now().toString(),
          timestamp: 'Just now',
          read: false
        }
        
        set((state) => ({
          notifications: [newNotification, ...state.notifications]
        }))
      },

      markAsRead: (id) => {
        set((state) => ({
          notifications: state.notifications.map((notification) =>
            notification.id === id
              ? { ...notification, read: true }
              : notification
          )
        }))
      },

      markAllAsRead: () => {
        set((state) => ({
          notifications: state.notifications.map((notification) => ({
            ...notification,
            read: true
          }))
        }))
      },

      removeNotification: (id) => {
        set((state) => ({
          notifications: state.notifications.filter((notification) => notification.id !== id)
        }))
      },

      clearAll: () => {
        set({ notifications: [] })
      },

      getUnreadCount: () => {
        return get().notifications.filter((notification) => !notification.read).length
      }
    }),
    {
      name: 'notifications-storage',
      partialize: (state) => ({ notifications: state.notifications })
    }
  )
)

// Helper functions to add specific types of notifications
export const addSuccessNotification = (title: string, message: string) => {
  useNotifications.getState().addNotification({
    type: 'success',
    title,
    message
  })
}

export const addErrorNotification = (title: string, message: string) => {
  useNotifications.getState().addNotification({
    type: 'error',
    title,
    message
  })
}

export const addWarningNotification = (title: string, message: string) => {
  useNotifications.getState().addNotification({
    type: 'warning',
    title,
    message
  })
}

export const addInfoNotification = (title: string, message: string) => {
  useNotifications.getState().addNotification({
    type: 'info',
    title,
    message
  })
}
