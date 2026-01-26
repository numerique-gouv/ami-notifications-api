import {
  PUBLIC_API_GEO_CITY_QUERY_BASE_URL,
  PUBLIC_API_GEO_CITY_QUERY_ENDPOINT,
  PUBLIC_API_GEO_COUNTRY_QUERY_BASE_URL,
  PUBLIC_API_GEO_COUNTRY_QUERY_ENDPOINT,
} from '$env/static/public'
import type { Address as AddressType } from '$lib/address'
import { Address } from '$lib/address'
import { callBAN } from '$lib/addressesFromBAN'
import * as auth from '$lib/auth'
import { franceConnectLogout, parseJwt } from '$lib/france-connect'
import { emit } from '$lib/nativeEvents'

type DataOrigin = 'user' | 'france-connect' | 'api-particulier' | 'cleared'

type DataDetail = {
  origin?: DataOrigin
  lastUpdate?: Date
}

export type DataDetails = {
  address: DataDetail
}

export type UserInfo = {
  sub: string
  gender: string
  birthdate: string
  birthcountry: string
  birthplace?: string
  given_name: string
  given_name_array: string[]
  family_name: string
  preferred_username?: string
  email: string
  aud: string
  exp: number
  iat: number
  iss: string
}

export type UserIdentity = {
  gender: string
  birthdate: string
  birthcountry?: string
  birthplace?: string
  given_name: string
  family_name: string
  preferred_username?: string | null
  email: string
  address?: AddressType
  scheduledNotificationsCreatedKeys: string[]
  dataDetails: DataDetails
}

class UserStore {
  connected: User | null = $state(null)

  async login(userinfo: UserInfo): Promise<User> {
    if (!userinfo) {
      throw new Error('No userinfo provided')
    }
    this.connected = new User(userinfo)
    await this.connected.updateIdentity()
    emit('user_logged_in', userinfo)
    return this.connected
  }

  async logout() {
    const id_token_hint = localStorage.getItem('id_token') || ''
    // Logout from AMI first: https://github.com/numerique-gouv/ami-notifications-api/issues/132
    localStorage.clear()
    this.connected = null
    await auth.logout()
    // And now logout from FC
    if (id_token_hint) {
      await franceConnectLogout(id_token_hint)
    }
  }

  async checkLoggedIn() {
    const userData = localStorage.getItem('user_data') || ''
    console.log('Checking if user is logged in', userData)
    if (userData !== '') {
      const userinfo: UserInfo = parseJwt(userData)
      console.log('User is logged in', userinfo)
      await this.login(userinfo)
    } else {
      this.connected = null
    }
  }
}

export class User {
  private _pivot: UserInfo = $state() as UserInfo
  private _identity: UserIdentity = $state() as UserIdentity

  constructor(userinfo: UserInfo) {
    this._pivot = userinfo
    // Load stored values that might have been updated by the user
    const storedIdentity = localStorage.getItem('user_identity') || '{}'
    const parsedIdentity = JSON.parse(storedIdentity)

    this._identity = {
      gender: this._pivot.gender,
      birthdate: this.formatBirthdate(this._pivot.birthdate),
      birthplace: parsedIdentity?.birthplace,
      birthcountry: parsedIdentity?.birthcountry,
      given_name: parsedIdentity?.given_name || this._pivot.given_name,
      family_name: this._pivot.family_name,
      preferred_username: this._pivot.preferred_username,
      email: parsedIdentity?.email || this._pivot.email,
      address: parsedIdentity?.address,
      scheduledNotificationsCreatedKeys:
        parsedIdentity?.scheduledNotificationsCreatedKeys || [],
      dataDetails: parsedIdentity?.dataDetails || {},
    }
    if (this._identity.address) {
      this._identity.address = Address.fromJSON(this._identity.address)
    }
    this._identity.dataDetails = {
      address: this._identity.dataDetails.address || {},
    }
  }

  get pivot() {
    return this._pivot
  }

  get identity() {
    return this._identity
  }

  setPreferredUsername(preferred_username: string) {
    if (preferred_username) {
      this._identity.preferred_username = preferred_username
    } else {
      delete this._identity.preferred_username
    }
    localStorage.setItem('user_identity', JSON.stringify(this.identity))
  }

  setEmail(email: string) {
    if (email) {
      this._identity.email = email
      localStorage.setItem('user_identity', JSON.stringify(this.identity))
    }
  }

  setAddress(address: AddressType | undefined, address_origin?: DataOrigin) {
    if (address) {
      this._identity.address = address
      this._identity.dataDetails.address.origin = address_origin || 'user'
    } else {
      delete this._identity.address
      this._identity.dataDetails.address.origin = 'cleared'
    }
    this._identity.dataDetails.address.lastUpdate = new Date()
    localStorage.setItem('user_identity', JSON.stringify(this.identity))
  }

  async setAddressFromAPIParticulier() {
    const encoded_address =
      localStorage.getItem('user_api_particulier_encoded_address') || ''
    if (encoded_address === '') {
      return
    }
    try {
      const decoded_address = JSON.parse(atob(encoded_address))
      const numero_libelle_voie = decoded_address.numero_libelle_voie || ''
      const lieu_dit = decoded_address.lieu_dit || ''
      const code_postal_ville = decoded_address.code_postal_ville || ''
      const inputValue = String(
        `${numero_libelle_voie} ${lieu_dit} ${code_postal_ville}`
      )
        .replace(/\s+/g, ' ')
        .trim()
      if (inputValue === '') {
        return
      }
      const response = await callBAN(inputValue)
      if (response.errorCode) {
        return
      }
      if (!response.results) {
        return
      }
      const first_result = response.results[0]
      const city = first_result.city
      const context = first_result.context
      const idBAN = first_result.id
      const label = first_result.label
      const name = first_result.name
      const postcode = first_result.postcode
      const address = new Address(city, context, idBAN, label, name, postcode)
      this.setAddress(address, 'api-particulier')
    } catch (error) {
      console.error(error)
    }
  }

  formatBirthdate(birthdate: string) {
    const date = new Date(birthdate)
    const options: Intl.DateTimeFormatOptions = {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }
    return date.toLocaleDateString('fr-FR', options)
  }

  addScheduledNotificationCreatedKey(key: string) {
    const scheduledNotificationsCreatedKeys = new Set(
      this._identity.scheduledNotificationsCreatedKeys
    )
    scheduledNotificationsCreatedKeys.add(key)
    this._identity.scheduledNotificationsCreatedKeys = [
      ...scheduledNotificationsCreatedKeys,
    ]
    localStorage.setItem('user_identity', JSON.stringify(this.identity))
  }

  clearScheduledNotificationCreatedKey() {
    this._identity.scheduledNotificationsCreatedKeys = []
    localStorage.setItem('user_identity', JSON.stringify(this.identity))
  }

  async updateIdentity() {
    if (!this._identity.birthplace && this._pivot.birthplace) {
      try {
        const birthplaceResponse = await fetch(
          `${PUBLIC_API_GEO_CITY_QUERY_BASE_URL}${PUBLIC_API_GEO_CITY_QUERY_ENDPOINT.replace('{birthplace}', this._pivot.birthplace)}`
        )
        const birthplaceJson = await birthplaceResponse.json()
        const birthplace = `${birthplaceJson.nom} (${this._pivot.birthplace.toString().slice(0, 2)})`
        this._identity.birthplace = birthplace
      } catch {}
    }
    if (!this._identity.birthcountry && this._pivot.birthcountry) {
      try {
        const birthcountryResponse = await fetch(
          `${PUBLIC_API_GEO_COUNTRY_QUERY_BASE_URL}${PUBLIC_API_GEO_COUNTRY_QUERY_ENDPOINT}${this._pivot.birthcountry}`
        )
        const birthcountryJson = await birthcountryResponse.json()
        const birthcountry = birthcountryJson?.data[0]?.LIBCOG
        this._identity.birthcountry = birthcountry
      } catch {}
    }
    if (!this._identity.dataDetails.address.origin) {
      await this.setAddressFromAPIParticulier()
    }
  }

  getInitials(): string {
    let initials_: string = ''
    if (this._pivot.given_name_array.length) {
      initials_ += this._pivot.given_name_array[0].substring(0, 1)
    }
    return initials_
  }
}

export const userStore = new UserStore()
