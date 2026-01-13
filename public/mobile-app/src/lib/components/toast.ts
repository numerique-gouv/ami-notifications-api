import { writable } from 'svelte/store'

export type Toast = {
  id: string
  title: string
  level: string
}

export const toasts = writable<Toast[]>([])

export const uniqueId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substring(2, 10)
}

export const addToast = (title: string, level: string) => {
  const id: string = uniqueId()
  const newToast: Toast = { id: id, title: title, level: level }
  toasts.update((current) => [...current, newToast])
  setTimeout(() => removeToast(id), 3000)
}

export const removeToast = (id: string) => {
  toasts.update((current) => current.filter((toast) => toast.id !== id))
}
