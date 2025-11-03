<script lang="ts">
import { parseJwt, franceConnectLogout } from '$lib/france-connect'
import { onMount } from 'svelte'
import {
  countUnreadNotifications,
  disableNotifications,
  enableNotifications,
  notificationEventsSocket,
} from '$lib/notifications'
import { getQuotientData } from '$lib/api-particulier'
import bankIcon from '@gouvfr/dsfr/dist/icons/buildings/bank-line.svg'

let userinfo: Object = $state({})
let quotientinfo: Object = $state({})
let unreadNotificationsCount: Number = $state(0)
let initials: String = $state('')
let isMenuDisplayed = $state(false)
let notificationsEnabled: boolean = $state(false)
let registration: Object = $state({})

const updateNotificationsEnabled = async (notificationsEnabledStatus) => {
  if (notificationsEnabledStatus === true) {
    registration = await enableNotifications()
  } else {
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

const getInitials = (given_name_array: []): String => {
  let initials_: String = ''
  given_name_array.forEach((given_name) => {
    initials_ += given_name.substring(0, 1)
  })
  return initials_
}

onMount(async () => {
  try {
    notificationsEnabled = localStorage.getItem('notifications_enabled') === 'true'
    await initializeNavigatorPermissions()

    const userData = localStorage.getItem('user_data')
    userinfo = parseJwt(userData)
    console.log($state.snapshot(userinfo))

    initials = getInitials(userinfo.given_name_array)

    unreadNotificationsCount = await countUnreadNotifications()
    notificationEventsSocket(async () => {
      unreadNotificationsCount = await countUnreadNotifications()
    })

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
  // And now logout from FC
  franceConnectLogout(id_token_hint)
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
      <div class="notification-svg-icon" id="message-icon">
        <img src="/remixicons/message-3.svg" alt="Icône de message" />
      </div>

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

  <div class="rubrique-container qr-code-scan-container">
    <div class="rubrique-content-container">
      <div class="fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
        <div class="fr-tile__body">
          <div class="fr-tile__content">
            <img class="qr-code-icon" src="/remixicons/qr-code.svg" alt="Icône de QR code" />
            <h3 class="fr-tile__title">
              <a href="/">Scanner le QR code d'un service partenaire</a>
            </h3>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="rubrique-container">
    <div class="header-container">
      <span class="title">Mes rendez-vous</span>
      <a title="Voir toutes mes rendez-vous" href="/">
        <span class="see-all">Voir tout</span>
        <img class="arrow-line" src="/remixicons/arrow-line.svg" alt="Icône de flèche" />
      </a>
    </div>
    <div class="rubrique-content-container">
      <div class="fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
        <div class="fr-tile__body">
          <div class="fr-tile__content">
            <h3 class="fr-tile__title">
              <a href="/#/rdv/">2 août 2025 à 15H15</a>
            </h3>
            <p class="fr-tile__desc">Rendez-vous dans votre Agence France Travail Paris 18e Ney</p>
            <div class="fr-tile__start">
              <p class="fr-badge">
                <img src="/remixicons/calendar-event-line.svg" alt="Icône de calendrier" />
                RDV
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="rubrique-container">
    <div class="header-container">
      <span class="title">Mes échéances</span>
      <a title="Voir toutes les échéances" href="/">
        <span class="see-all">Voir tout</span>
        <img class="arrow-line" src="/remixicons/arrow-line.svg" alt="Icône de flèche" />
      </a>
    </div>
    <div class="rubrique-content-container">
      <div class="fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
        <div class="fr-tile__body">
          <div class="fr-tile__content">
            <h3 class="fr-tile__title">
              <a href="/">Ramassage encombrants</a>
            </h3>
            <p class="fr-tile__desc">Le ramassage mensuel des encombrants aura lieu ce jeudi 4 avril</p>
            <div class="fr-tile__start">
              <p class="fr-badge">
                <img src="{bankIcon}" alt="Icône de banque" />
                Municipalité
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="rubrique-container">
    <div class="header-container">
      <span class="title">Mes demandes</span>
      <a title="Voir toutes les demandes" href="/">
        <span class="see-all">Voir tout</span>
        <img class="arrow-line" src="/remixicons/arrow-line.svg" alt="Icône de flèche" />
      </a>
    </div>
    <div class="rubrique-content-container">
      TODO
    </div>
  </div>

  <section class="fr-accordion">
    <h3 class="fr-accordion__title">
      <button type="button" class="fr-accordion__btn" aria-expanded="false" aria-controls="accordion-1">Données de debug</button>
    </h3>
    <div id="accordion-1" class="fr-collapse">
      <ul>
        <li>userinfo: <pre>{ JSON.stringify(userinfo, null, 2) }</pre></li>
        <li>sub: { userinfo.sub }</li>
        <li>given_name: { userinfo.given_name }</li>
        <li>given_name_array: { userinfo.given_name_array }</li>
        <li>family_name: { userinfo.family_name }</li>
        <li>birthdate: { userinfo.birthdate }</li>
        <li>gender: { userinfo.gender }</li>
        <li>birthplace: { userinfo.birthplace }</li>
        <li>birthcountry: { userinfo.birthcountry }</li>
        <li>email: { userinfo.email }</li>
        <li>aud: { userinfo.aud }</li>
        <li>exp: { userinfo.exp }</li>
        <li>iat: { userinfo.iat }</li>
        <li>iss: { userinfo.iss }</li>
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

    .qr-code-scan-container {
      .fr-tile {
        background-color: var(--blue-france-950-100);

        .fr-tile__content {
          display: flex;
          flex-direction: row;
          align-items: center;

          img {
            margin-right: 24px;
          }

          .fr-tile__title {
            margin-bottom: 0;

            a {
              color: var(--grey-50-1000);
              font-size: 16px;
              font-weight: 500;
              line-height: 24px;
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
        }
      }

      .rubrique-content-container {
        .fr-tile {
          .fr-badge {
            font-size: 12px;
            font-weight: 700;
            line-height: 20px;
            color: var(--success-425-625);
            background-color: var(--green-bourgeon-975-75);

            img {
              width: 12px;
              margin-right: 4px;
            }
          }
        }
      }
    }

    .fr-accordion {
      margin-bottom: 24px;
    }
  }
</style>
