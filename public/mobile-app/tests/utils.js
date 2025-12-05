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

export const mockUserInfo = {
  sub: 'fake sub',
  given_name: 'Angela Claire Louise',
  given_name_array: ['Angela', 'Claire', 'Louise'],
  family_name: 'DUBOIS',
  email: 'some@email.com',
  birthdate: '1962-08-24',
  birthcountry: '99100',
  birthplace: '75100',
  gender: 'female',
  aud: 'fake aud',
  exp: 1753877658,
  iat: 1753877598,
  iss: 'https://fcp-low.sbx.dev-franceconnect.fr/api/v2',
}
