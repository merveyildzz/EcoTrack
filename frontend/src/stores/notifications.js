import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref([])
  let notificationId = 0

  const addNotification = (message, type = 'info', duration = 5000) => {
    const id = ++notificationId
    const notification = { id, message, type, duration }
    
    notifications.value.push(notification)
    
    // Auto-remove after duration
    setTimeout(() => {
      removeNotification(id)
    }, duration)
    
    return id
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value = []
  }

  // Convenience methods
  const success = (message, duration) => addNotification(message, 'success', duration)
  const error = (message, duration) => addNotification(message, 'error', duration)
  const info = (message, duration) => addNotification(message, 'info', duration)

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    info
  }
})