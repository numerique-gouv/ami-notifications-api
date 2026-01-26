import { vi } from 'vitest'
import { Address } from '$lib/address'
import { User } from '$lib/state/User.svelte'

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

export const mockUserInfoWithPreferredUsername = {
  sub: 'fake sub',
  given_name: 'Pierre',
  given_name_array: ['Pierre'],
  family_name: 'MERCIER',
  preferred_username: 'DUBOIS',
  email: 'some-other@email.com',
  birthdate: '1969-03-17',
  birthcountry: '99100',
  birthplace: '95277',
  gender: 'male',
  aud: 'fake aud',
  exp: 1766064161,
  iat: 1766064102,
  iss: 'https://fcp-low.sbx.dev-franceconnect.fr/api/v2',
}

export const mockAddress: Address = new Address(
  'Paris',
  '75, Paris, Île-de-France',
  '75107_8909',
  'Avenue de Ségur 75007 Paris',
  'Avenue de Ségur',
  '75007'
)

export const mockUserIdentity = {
  gender: 'female',
  birthdate: '1962-08-24',
  given_name: 'Angela Claire Louise',
  family_name: 'DUBOIS',
  email: 'wossewodda-3728@yopmail.com',
  address: mockAddress,
  birthplace: 'Paris 7e Arrondissement (75)',
  birthcountry: 'France',
  dataDetails: { address: { origin: 'user' } },
}

export const mockUser = new User(mockUserInfo)
export const mockUserWithPreferredUsername = new User(mockUserInfoWithPreferredUsername)
