<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import type { Notification } from '$lib/notifications'
  import {
    notificationEventsSocket,
    readNotification,
    retrieveNotifications,
  } from '$lib/notifications'
  import { prettyDate } from '$lib/prettyDate'
  import { userStore } from '$lib/state/User.svelte'

  let notifications: Notification[] = $state([])

  onMount(async () => {
    if (!userStore.connected) {
      goto('/')
    }

    notifications = await retrieveNotifications()
    notificationEventsSocket(async () => {
      notifications = await retrieveNotifications()
    })
  })

  const markNotificationAsRead = async (event: MouseEvent, notificationId: string) => {
    event.preventDefault()
    let result = await readNotification(notificationId)
  }

  const navigateToPreviousPage = async () => {
    window.history.back()
  }

  const goToSettings = () => {
    goto('/#/settings')
  }
</script>

<nav>
  <div class="back-button-wrapper">
    <button onclick={navigateToPreviousPage}
            title="Retour à la page précédente"
            aria-label="Retour à la page précédente"
            data-testid="back-button"
    >
      <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
    </button>
  </div>
  <div class="title">
    <h2>Notifications</h2>
    <div class="settings-svg-icon">
      <button class="fr-btn fr-btn--tertiary"
              type="button"
              onclick="{goToSettings}"
              data-testid="settings-button"
      >
        <img src="/remixicons/settings.svg" alt="Icône de paramétrage" />
        Gérer
      </button>
    </div>
  </div>
</nav>

<div class="notifications-content-container">
  {#each notifications as notification}
  <div class="fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link notification {notification.read ? 'read': ''}" data-testid="notification-{notification.id}">
    <div class="fr-tile__header">
      <span class="notification__status {notification.read ? 'read': ''}" aria-hidden="true"><i>•</i></span>
      <span class="notification__icon {notification.content_icon ? notification.content_icon: 'fr-icon-information-line'}" aria-hidden="true"></span>
    </div>
    <div class="fr-tile__body">
      <div class="fr-tile__content">
        <div class="notification__title">
          <h3 class="fr-tile__title">
            <a href="/" onclick={(event) => markNotificationAsRead(event, notification.id)} data-testid="notification-link-{notification.id}">{notification.content_title}</a>
          </h3>
          <span class="notification__age">
            {prettyDate(notification.created_at)}
          </span>
        </div>
        <p class="fr-tile__desc">{notification.content_body}</p>
      </div>
    </div>
  </div>
  {/each}
</div>

<style>
  nav {
    padding: 1.5rem 1rem;
    .back-button-wrapper {
      margin-bottom: .5rem;
      color: var(--text-active-blue-france);
      button {
        padding: 0;
      }
    }
    .title {
      display: flex;
      h2 {
        flex-grow: 1;
        margin-bottom: 0;
      }
      .settings-svg-icon {
        padding-top: .25rem;
        color: var(--text-active-blue-france);
        img {
          margin-right: .5rem;
          width: 1rem;
          height: 1rem;
        }
      }
    }
  }
  .notifications-content-container {
    .notification {
      background: none;
      border-bottom: 1px solid var(--background-alt-grey-active);
      padding: .75rem;
      &:not(.read) {
        background-color: var(--background-contrast-blue-france);
      }
      .fr-tile__header {
        display: flex;
        margin-right: .75rem;
        .notification__status {
          width: 1rem;
          font-size: 22px;
          color: var(--red-marianne-main-472);
          &.read i {
            display: none;
          }
        }
        .notification__icon {
          line-height: 2rem;
          color: var(--blue-france-sun-113-625);
          &::before {
            --icon-size: 1.25rem;
          }
        }
      }
      .fr-tile__content {
        padding-bottom: 0;
        .notification__title {
          display: flex;
          align-items: center;
          width: 100%;
          .fr-tile__title {
            order: 1;
            width: 100%;
            margin-bottom: 0;
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
            font-size: .75rem;
            color: var(--text-mention-grey);
            width: 2rem;
            text-align: right;
          }
        }
        .fr-tile__desc {
          font-size: 12px;
          line-height: 1.25rem;
          color: var(--text-black-white-grey);
        }
      }
    }
  }
</style>
