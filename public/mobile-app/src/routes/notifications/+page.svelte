<script lang="ts">
import { PUBLIC_API_URL } from '$env/static/public'
import { onMount } from 'svelte'
import { goto } from '$app/navigation'
import { prettyDate } from '$lib/prettyDate.ts'
import { retrieveNotifications } from '$lib/notifications'

type Notification = {
  id: number
  user_id: number
  title: string
  date: Date
  message: string
  sender: string
}

let isFranceConnected: boolean = $state(false)
let notifications: [Notification] = $state(localStorage.getItem('notification') || [])

onMount(async () => {
  isFranceConnected = !!localStorage.getItem('access_token')
  if (!isFranceConnected) {
    goto('/')
  }

  notifications = await retrieveNotifications()
})
</script>

<nav class="fr-p-4v fr-pt-6v">
  <div class="back-link fr-mb-2v">
    <a href="/" title="Retour à la page d'accueil" aria-label="Retour à la page d'accueil">
      <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
    </a>
  </div>
  <div class="title">
    <h2 class="fr-mb-0">Notifications</h2>
    <div class="settings-svg-icon fr-pt-1v">
      <img src="/remixicons/settings.svg" alt="Icône de paramétrage" class="fr-mr-2v" />
    </div>
  </div>
</nav>

<div class="notifications-content-container">
  {#each notifications as notification}
  <div class="fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link fr-p-3v notification {notification.status}">
    <div class="fr-tile__header">
      <span class="notification__status {notification.status}" aria-hidden="true"><i>•</i></span>
      <span class="notification__icon fr-icon-calendar-event-fill" aria-hidden="true"></span>
    </div>
    <div class="fr-tile__body">
      <div class="fr-tile__content fr-pb-0">
        <div class="notification__title">
          <h3 class="fr-tile__title fr-mb-0">
            <a href="/">{notification.sender} : {notification.title}</a>
          </h3>
          <span class="notification__age">
            {prettyDate(notification.date)}
          </span>
        </div>
        <p class="fr-tile__desc">{notification.message}</p>
      </div>
    </div>
  </div>
  {/each}
</div>

<style>
  nav {
    .back-link {
      color: var(--text-active-blue-france);
      a {
        text-decoration: none;
        --underline-img: none;
      }
    }
    .title {
      display: flex;
      h2 {
        flex-grow: 1;
      }
      .settings-svg-icon {
        color: var(--text-active-blue-france);
        img {
          width: 20px;
          height: 20px;
        }
      }
    }
  }
  .notifications-content-container {
    .notification {
      background: none;
      border-bottom: 1px solid var(--background-alt-grey-active);
      &.unread {
        background-color: var(--background-contrast-blue-france);
      }
      .fr-tile__header {
        display: flex;
        margin-right: 12px;
        .notification__status {
          width: 16px;
          font-size: 22px;
          color: var(--red-marianne-main-472);
          &:not(.unread) i {
            display: none;
          }
        }
        .notification__icon {
          line-height: 32px;
          color: var(--blue-france-sun-113-625);
          &::before {
            --icon-size: 20px;
          }
        }
      }
      .notification__title {
        display: flex;
        align-items: center;
        width: 100%;
        .fr-tile__title {
          order: 1;
          width: 100%;
          &::before {
            background: none;
          }
          a {
            font-size: 14px;
            color: var(--text-black-white-grey);
            &::before {
              background: none;
            }
            &::after {
              width: 0;
            }
          }
        }
        .notification__age {
          order: 2;
          font-size: 12px;
          color: var(--text-mention-grey);
          width: 32px;
          text-align: right;
        }
      }
    }
    .fr-tile__desc {
      font-size: 12px;
      line-height: 20px;
      color: var(--text-black-white-grey);
    }
  }
</style>
