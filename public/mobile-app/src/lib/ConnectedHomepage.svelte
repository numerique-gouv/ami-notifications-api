<script lang="ts">
import { parseJwt, franceConnectLogout } from '$lib/france-connect'
import type { UserInfo } from '$lib/france-connect'
import { onMount } from 'svelte'
import {
  countUnreadNotifications,
  disableNotifications,
  enableNotifications,
  notificationEventsSocket,
} from '$lib/notifications'
import type { Registration } from '$lib/registration'
import { getQuotientData } from '$lib/api-particulier'
import { PUBLIC_API_URL } from '$env/static/public'
import { buildAgenda } from '$lib/agenda'
import type { Agenda } from '$lib/agenda'
import AgendaItem from '$lib/AgendaItem.svelte'

let userinfo: UserInfo | null = $state(null)
let quotientinfo: Object = $state({})
let unreadNotificationsCount: number = $state(0)
let initials: string = $state('')
let isMenuDisplayed: boolean = $state(false)
let isAddressEmpty: boolean = $state(true)
let notificationsEnabled: boolean = $state(false)
let registration: Registration | null = $state(null)
let agenda: Agenda | null = $state(null)

const updateNotificationsEnabled = async (notificationsEnabledStatus: boolean) => {
  if (notificationsEnabledStatus === true) {
    registration = await enableNotifications()
  } else if (registration) {
    await disableNotifications(registration.id)
  }
  notificationsEnabled = notificationsEnabledStatus
  localStorage.setItem('notifications_enabled', notificationsEnabledStatus.toString())
}

const initializeNavigatorPermissions = async () => {
  if (navigator.permissions) {
    const permissionStatus = await navigator.permissions.query({
      name: 'notifications',
    })

    permissionStatus.onchange = async () => {
      await updateNotificationsEnabled(permissionStatus.state == 'granted')
      console.log(`notifications permission status is ${permissionStatus.state}`)
    }
  }
}

const getInitials = (given_name_array: string[]): string => {
  let initials_: string = ''
  given_name_array.forEach((given_name) => {
    initials_ += given_name.substring(0, 1)
  })
  return initials_
}

onMount(async () => {
  try {
    isAddressEmpty = localStorage.getItem('user_address') === ''
    notificationsEnabled = localStorage.getItem('notifications_enabled') === 'true'
    await initializeNavigatorPermissions()

    const userData = localStorage.getItem('user_data') || ''
    userinfo = parseJwt(userData)
    console.log($state.snapshot(userinfo))

    initials = getInitials(userinfo?.given_name_array)

    unreadNotificationsCount = await countUnreadNotifications()
    notificationEventsSocket(async () => {
      unreadNotificationsCount = await countUnreadNotifications()
    })

    agenda = await buildAgenda()
    console.log($state.snapshot(agenda))

    quotientinfo = await getQuotientData()
    console.log($state.snapshot(quotientinfo))
  } catch (error) {
    console.error(error)
  }
})

const toggleMenu = () => {
  isMenuDisplayed = !isMenuDisplayed
}

const clickEnableNotifications = async () => {
  await updateNotificationsEnabled(true)
}

const clickDisableNotifications = async () => {
  await updateNotificationsEnabled(false)
}

const logout = async () => {
  const id_token_hint = localStorage.getItem('id_token') || ''
  // Logout from AMI first: https://github.com/numerique-gouv/ami-notifications-api/issues/132
  localStorage.clear()
  try {
    // delete auth cookie
    await fetch(`${PUBLIC_API_URL}/logout`, {
      method: 'POST',
      credentials: 'include',
    })
  } catch (error) {
    console.error(error)
  }
  // And now logout from FC
  await franceConnectLogout(id_token_hint)
}
</script>

<div class="homepage-connected">
  <div class="header">
    <button
      class="header-left"
      onclick={toggleMenu}
      data-testid="toggle-menu-button"
    >
      <span class="user-profile">
        {initials}
      </span>
    </button>

    <div class="header-right">
      <div class="notification-svg-icon" id="notification-icon">
        <a href="/#/notifications">
          <img src="/remixicons/notification-3.svg" alt="Icône de notifications" />
          <div class="count-number-wrapper" data-content="{unreadNotificationsCount}">
            {unreadNotificationsCount}
          </div>
        </a>
      </div>
    </div>
  </div>

  <div class="menu {isMenuDisplayed ? '' : 'is-hidden'}">
    <div class="container">
      {#if notificationsEnabled}
        <button
            type="button"
            onclick={clickDisableNotifications}
            data-testid="disable-notifications"
        >
          Ne plus recevoir de notifications sur ce terminal
        </button>
      {:else}
        <button
            type="button"
            onclick={clickEnableNotifications}
            data-testid="enable-notifications"
        >
          Recevoir des notifications sur ce terminal
        </button>
      {/if}

      <button
          class="fr-connect-logout"
          type="button"
          onclick={logout}
      >
        <span>Me déconnecter</span>
      </button>
    </div>
  </div>

  {#if isAddressEmpty}
    <div class="rubrique-container address-container">
      <div class="rubrique-content-container">
        <div class="fr-tile fr-tile-sm fr-tile--horizontal fr-tile--no-border fr-enlarge-link">
          <div class="fr-tile__body">
            <div class="fr-tile__content">
              <img class="address-icon" src="/remixicons/house.svg" alt="Icône adresse" />
              <h3 class="fr-tile__title">
                <a href="/#/adresse"><b>Gagnez du temps</b> en <b>renseignant votre adresse</b> une seule fois !</a>
              </h3>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <div class="rubrique-container agenda-container">
    <div class="header-container">
      <span class="title">Mon agenda</span>
      <a class="see-all" title="Voir tous mes évènements" href="/#/agenda">
        <span>Voir tout</span>
        <img class="arrow-line" src="/remixicons/arrow-line.svg" alt="Icône de flèche" />
      </a>
    </div>
    <div class="rubrique-content-container">
    {#if agenda}
      {#if agenda.now.length}
        <AgendaItem item={agenda.now[0]} displayDate={false} />
      {:else if agenda.next.length}
        <AgendaItem item={agenda.next[0]} displayDate={false} />
      {/if}
    {/if}
    </div>
  </div>

  <div class="rubrique-container requests-container">
    <div class="header-container">
      <span class="title">Mes demandes</span>
      <span class="see-all">
        <span>Voir tout</span>
        <img class="arrow-line" src="/remixicons/arrow-line-disabled.svg" alt="Icône de flèche" />
      </span>
    </div>
    <div class="rubrique-content-container">
      <div class="no-requests">
        <div class="no-requests--icon">
          <img class="address-icon" src="/remixicons/tracking.svg" alt="Icône de suivi" />
        </div>
        <div class="no-request--title">
          Retrouvez et suivez vos démarches ici
        </div>
      </div>
    </div>
  </div>

  <section class="fr-accordion">
    <h3 class="fr-accordion__title">
      <button type="button" class="fr-accordion__btn" aria-expanded="false" aria-controls="accordion-1">Données de debug</button>
    </h3>
    <div id="accordion-1" class="fr-collapse">
      <ul>
        <li>userinfo: <pre>{ JSON.stringify(userinfo, null, 2) }</pre></li>
        <li>sub: { userinfo?.sub }</li>
        <li>given_name: { userinfo?.given_name }</li>
        <li>given_name_array: { userinfo?.given_name_array }</li>
        <li>family_name: { userinfo?.family_name }</li>
        <li>birthdate: { userinfo?.birthdate }</li>
        <li>gender: { userinfo?.gender }</li>
        <li>birthplace: { userinfo?.birthplace }</li>
        <li>birthcountry: { userinfo?.birthcountry }</li>
        <li>email: { userinfo?.email }</li>
        <li>aud: { userinfo?.aud }</li>
        <li>exp: { userinfo?.exp }</li>
        <li>iat: { userinfo?.iat }</li>
        <li>iss: { userinfo?.iss }</li>
        <li>quotientinfo: <pre>{ JSON.stringify(quotientinfo, null, 2) }</pre></li>
      </ul>
    </div>
  </section>
</div>

<style>
  .is-hidden {
    display: none;
  }

  .homepage-connected {
    margin: 24px 16px;

    .header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 24px;

      .header-left {
        display: flex;
        justify-content: center;
        align-items: center;

        height: 48px;
        width: 48px;
        border-radius: 50%;
        background-color: var(--blue-france-925-125-hover);

        .user-profile {
          font-size: 18px;
          font-weight: 500;
          line-height: 28px;
          color: var(--blue-france-sun-113-625);
        }
      }

      .header-right {
        display: flex;
        align-items: center;

        .notification-svg-icon {
          margin-right: 16px;
          position: relative;

          & a[href]{
            background: none;
          }

          .count-number-wrapper {
            position: absolute;
            top: 0;
            left: .75rem;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 1rem;
            height: 1rem;
            border-radius: .5rem;
            background-color: #E1000F;
            color: white;
            font-size: .75rem;

            &[data-content="0"] {
              display: none;
            }
          }
        }
      }
    }

    .menu {
      position: absolute;
      z-index: 1000;

      margin-top: -20px;
      padding: 8px;
      background-color: white;
      border-radius: 4px;
      box-shadow: 2px 2px 2px gray;

      .container {
        display: flex;
        flex-direction: column;
        align-items: start;

        button {
          padding: 8px 12px;

          font-size: 14px;
          line-height: 24px;
        }
      }
    }

    .address-container {
      .fr-tile {
        background-color: var(--blue-france-950-100);
        padding: 1.5rem 1.5rem 1rem 1.5rem;

        .fr-tile__content {
          display: flex;
          flex-direction: row;
          align-items: center;
          padding-bottom: 1rem;

          img {
            margin-right: 0.5rem;
          }

          .fr-tile__title {
            font-size: 16px;
            line-height: 24px;
            font-weight: 400;
            a {
              color: var(--grey-0-1000);
              &::after {
                color: var(--text-active-blue-france);
                bottom: 1.25rem;
                right: 1.25rem;
                --icon-size: 1rem;
              }
            }
          }
        }
      }
    }

    .rubrique-container {
      margin-bottom: 24px;

      .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .title {
          font-size: 18px;
          font-weight: 500;
          line-height: 28px;
        }

        .see-all {
          font-size: 14px;
          font-weight: 400;
          line-height: 24px;
          color: var(--blue-france-sun-113-625);
          margin-right: 4px;
          display: inline-flex;
          gap: 4px;
        }
        span.see-all {
          color: var(--text-disabled-grey);
          img {
            color: var(--text-disabled-grey);
          }
        }
      }
    }

    .requests-container {
      .no-requests {
        padding: 1rem;
        display: flex;
        flex-direction: column;
        text-align: center;
        font-size: 16px;
        line-height: 24px;
        color: var(--grey-0-1000);
        img {
          height: 5rem;
          width: 5rem;
        }
      }
    }

    .fr-accordion {
      margin-bottom: 24px;
    }
  }
</style>
