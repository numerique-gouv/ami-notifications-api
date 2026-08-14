<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import NotificationIcon from '$lib/components/NotificationIcon.svelte';
  import type { AppNotification } from '$lib/notifications';
  import {
    notificationEventsSocket,
    readNotification,
    retrieveNotifications,
  } from '$lib/notifications';
  import { prettyDate } from '$lib/prettyDate';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';
  let notifications: AppNotification[] = $state([]);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
      return;
    }

    notifications = await retrieveNotifications();
    notificationEventsSocket(async () => {
      console.log('New message received from the websocket, retrieving notifications');
      notifications = await retrieveNotifications();
    });
  });

  const redirectToLink = (notificationItemExternalUrl: string) => {
    if (notificationItemExternalUrl) {
      window.location.href = notificationItemExternalUrl;
    }
  };

  const clickOnNotification = async (
    event: MouseEvent,
    notificationId: string,
    notificationItemExternalUrl: string
  ) => {
    event.preventDefault();
    await readNotification(notificationId);
    redirectToLink(notificationItemExternalUrl);
  };

  const goToSettings = () => {
    goto('/#/preferences/notifications');
  };
</script>

<NavWithBackButton title="Notifications" {backUrl}>
  <div class="settings-svg-icon">
    <button
      type="button"
      class="fr-btn fr-icon-settings-3-line fr-btn--icon-left fr-btn--tertiary"
      onclick="{goToSettings}"
      data-testid="settings-button"
      aria-label="Gérer les notifications"
    >
      Gérer
    </button>
  </div>
</NavWithBackButton>

<div class="notifications-content-container fr-pt-14w">
  {#each notifications as notification}
    <div
      class="fr-tile fr-tile--sm fr-tile--horizontal fr-enlarge-button fr-p-3v notification {notification.read ? 'read': ''}"
      data-testid="notification-{notification.id}"
    >
      <div class="fr-tile__header fr-mr-3v">
        <span
          class="notification__status {notification.read ? 'read': ''}"
          aria-hidden="true"
          ><i>•</i></span
        >
        <NotificationIcon
          icon={notification.content_icon}
          defaultIcon="fr-icon-information-line"
        />
      </div>
      <div class="fr-tile__body">
        <div class="fr-tile__content fr-pb-0">
          <div class="notification__title">
            <h3 class="fr-tile__title fr-mb-0">
              <button
                type="button"
                class="fr-text--sm"
                onclick={(event) => clickOnNotification(event, notification.id, notification.url)}
                data-testid="notification-link-{notification.id}"
              >
                {notification.content_title}
              </button>
            </h3>
            <span class="notification__age fr-text--xs">
              {prettyDate(notification.created_at)}
            </span>
          </div>
          <p class="fr-tile__desc fr-text--xs">{notification.content_body}</p>
        </div>
      </div>
    </div>
  {/each}
</div>

<style>
  .notifications-content-container {
    .notification {
      background-color: var(--background-contrast-blue-france);
      border-bottom: 1px solid var(--background-alt-grey-active);
      &.read {
        background: none;
        .notification__status i {
          display: none;
        }
      }
      .fr-tile__header {
        display: flex;
        .notification__status {
          width: 1rem;
          font-size: 22px;
          color: var(--red-marianne-main-472);
        }
      }
      .fr-tile__content {
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
            button {
              color: var(--text-title-grey);
              &::before {
                background: none;
              }
              &::after {
                display: none;
              }
            }
          }
          .notification__age {
            order: 2;
            color: var(--text-mention-grey);
            width: 2rem;
            text-align: right;
          }
        }
      }
    }
  }
</style>
