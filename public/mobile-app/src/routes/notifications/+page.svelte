<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import NotificationIcon from '$lib/components/NotificationIcon.svelte';
  import { buildFollowup, Followup, FollowupItem } from '$lib/followup';
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
  let followup: Followup | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
    followup = await buildFollowup();

    notifications = await retrieveNotifications();
    notificationEventsSocket(async () => {
      console.log('New message received from the websocket, retrieving notifications');
      notifications = await retrieveNotifications();
      followup = await buildFollowup();
    });
  });

  const redirectToLink = (notification: AppNotification) => {
    let item: FollowupItem | null = null;
    if (followup && notification.item_parent_id) {
      item = followup.findItem(
        notification.item_parent_partner_id || '',
        notification.item_parent_type || '',
        notification.item_parent_id || ''
      );
    }
    if (followup && !item && notification.item_id) {
      // parent item can be unknown and item displayed as a parent
      item = followup.findItem(
        notification.partner_id,
        notification.item_type || '',
        notification.item_id || ''
      );
    }
    if (item) {
      AMIGoto(item.getItemDetailPageUrl());
      return;
    }
    if (notification.url) {
      AMIGoto(notification.url);
    }
  };

  const clickOnNotification = async (
    event: MouseEvent,
    notification: AppNotification
  ) => {
    event.preventDefault();
    await readNotification(notification.id);
    redirectToLink(notification);
  };

  const goToSettings = () => {
    AMIGoto('/#/preferences/notifications');
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
      class="fr-tile fr-tile--sm fr-tile--horizontal fr-tile--no-border fr-tile--no-icon fr-enlarge-button fr-p-3v notification {notification.read ? 'read': 'fr-background-contrast--blue-france'}"
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
                onclick={(event) => clickOnNotification(event, notification)}
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
