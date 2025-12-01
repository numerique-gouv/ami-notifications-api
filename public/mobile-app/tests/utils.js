import { vi } from 'vitest'

export const mockPushSubscription = {
  unsubscribe: () => Promise.resolve(true),
  endpoint: '',
  expirationTime: 0,
  options: {
    applicationServerKey: null,
    userVisibleOnly: true,
  },
  getKey: vi.fn(),
  toJSON: vi.fn(),
}
