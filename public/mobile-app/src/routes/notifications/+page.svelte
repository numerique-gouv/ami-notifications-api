<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { AMIGoto } from '$lib/ami-goto';
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
      AMIGoto(notificationItemExternalUrl);
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
      class="fr-tile fr-tile--sm fr-tile--horizontal fr-tile--no-border fr-tile--no-icon fr-enlarge-button fr-p-3v notification {notification.read ? 'readed': 'fr-background-contrast--blue-france'}"
      data-testid="notification-{notification.id}"
    >
      <div class="fr-tile__header fr-mr-3v">
        <span class="notification__status" aria-hidden="true"
          ><i class={notification.read ? 'fr-hidden': ''}>•</i></span
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
                class="fr-text--sm fr-text-title--grey"
                onclick={(event) => clickOnNotification(event, notification.id, notification.url)}
                data-testid="notification-link-{notification.id}"
              >
                {notification.content_title}
              </button>
            </h3>
            <span class="notification__age fr-text-mention--grey fr-text--xs">
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
      border-bottom: 1px solid var(--background-alt-grey-active);
      .fr-tile__header {
        display: flex;
        .notification__status {
          width: 1rem;
          font-size: 22px;
          color: var(--red-marianne-main-472);
        }
      }
      .notification__title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        width: 100%;
        .fr-tile__title button:before,
        .fr-tile__title button,
        .fr-tile__title:before {
          background: none;
        }
        .notification__age {
          order: 2;
        }
      }
    }
  }
</style>
