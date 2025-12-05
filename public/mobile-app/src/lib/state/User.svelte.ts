import { franceConnectLogout, parseJwt } from '$lib/france-connect'
import * as auth from '$lib/auth'

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
}

class UserStore {
  connected: User | null = $state(null)

  async login(userinfo: UserInfo): Promise<User> {
    if (!userinfo) {
      throw new Error('No userinfo provided')
    }
    this.connected = new User(userinfo)
    await this.connected.updateIdentity()
    return this.connected
  }

  async logout() {
    const id_token_hint = localStorage.getItem('id_token') || ''
    // Logout from AMI first: https://github.com/numerique-gouv/ami-notifications-api/issues/132
    localStorage.clear()
    this.connected = null
    await auth.logout()
    // And now logout from FC
    await franceConnectLogout(id_token_hint)
  }

  isConnected(): boolean {
    return !!this.connected
  }

  async checkLoggedIn() {
    const userData = localStorage.getItem('user_data') || ''
    console.log('Checking if user is logged in', userData)
    if (userData != '') {
      const userinfo: UserInfo = parseJwt(userData)
      console.log('User is logged in', userinfo)
      await userStore.login(userinfo)
    } else {
      this.connected = null
    }
  }
}

export class User {
  private _pivot: UserInfo
  private _identity: UserIdentity

  constructor(userinfo: UserInfo) {
    this._pivot = userinfo
    this._identity = {
      gender: this._pivot.gender,
      birthdate: this._pivot.birthdate,
      given_name: this._pivot.given_name,
      family_name: this._pivot.family_name,
      preferred_username: this._pivot.preferred_username,
      email: this._pivot.email,
    }
  }

  get pivot() {
    return this._pivot
  }

  get identity() {
    return this._identity
  }

  set identity(value: UserIdentity) {
    this._identity = value
  }

  async updateIdentity() {
    if (this._pivot.birthplace) {
      const birthplaceResponse = await fetch(
        `https://geo.api.gouv.fr/communes/${this._pivot.birthplace}?fields=nom&format=json`
      )
      const birthplaceJson = await birthplaceResponse.json()
      const birthplace = `${birthplaceJson.nom} (${this._pivot.birthplace.toString().slice(0, 2)})`
      this._identity.birthplace = birthplace
    }
    if (this._pivot.birthcountry) {
      const birthcountryResponse = await fetch(
        `https://tabular-api.data.gouv.fr/api/resources/3580bf65-1d11-4574-a2ca-903d64ad41bd/data/?page=1&page_size=20&COG__exact=${this._pivot.birthcountry}`
      )
      const birthcountryJson = await birthcountryResponse.json()
      const birthcountry = birthcountryJson?.data[0]?.LIBCOG
      this._identity.birthcountry = birthcountry
    }
  }

  getInitials(): string {
    let initials_: string = ''
    this._pivot.given_name_array.forEach((given_name) => {
      initials_ += given_name.substring(0, 1)
    })
    return initials_
  }
}

export const userStore = new UserStore()
