<script lang="ts">
  import { onMount } from 'svelte';
  import { PUBLIC_SKELETON_DEBUG_DELAY } from '$env/static/public';
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

  const waitForPageData = async () => {
    if (PUBLIC_SKELETON_DEBUG_DELAY) {
      await new Promise((resolve) => {
        setTimeout(() => resolve(0), parseFloat(PUBLIC_SKELETON_DEBUG_DELAY));
      });
    }
    [followup, notifications] = await Promise.all([
      buildFollowup(),
      retrieveNotifications(),
    ]);

    notificationEventsSocket(async () => {
      console.log('New message received from the websocket, retrieving notifications');
      notifications = await retrieveNotifications();
      followup = await buildFollowup();
    });
  };

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
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

{#if userStore.connected}
  <div class="notifications-content-container fr-pt-14w">
    {#await waitForPageData()}
      <div class="skeleton">
        {#each Array(7).keys() as i}
          <div
            class="notification-line fr-tile fr-tile--sm fr-tile--horizontal fr-tile--no-border fr-tile--no-icon fr-enlarge-button fr-p-3v"
          >
            <div class="icon"></div>
            <div class="content">
              <div class="line1"></div>
              <div class="line2"></div>
            </div>
          </div>
        {/each}
      </div>
    {:then pageDataLoaded}
      {#each notifications as notification}
        <div
          class="fr-tile fr-tile--sm fr-tile--horizontal fr-tile--no-border fr-tile--no-icon fr-enlarge-button fr-p-3v notification {notification.read ? 'read': 'fr-background-contrast--blue-france'}"
          data-testid="notification-{notification.id}"
        >
          <div class="fr-tile__header fr-mr-3v">
            <span class="notification__status">
              {#if notification.read}
                <span class="fr-sr-only">Lu</span>
              {:else}
                <i>•</i>
                <span class="fr-sr-only">Non lu</span>
              {/if}
            </span>
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
    {/await}
  </div>
{/if}

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
  .skeleton {
    .notification-line {
      display: flex;
      padding: 0.75rem 0;
      border-bottom: 1px solid #dddddd;
      .icon {
        margin: 0 1rem 0 1rem;
        height: 1.5rem;
        width: 1.5rem;
        border-radius: 100%;
        background: #e3e3fd;
      }
      .content {
        flex: 1;
      }
      .line1 {
        background: #ececfe;
        width: 100%;
        height: 1rem;
        margin-bottom: 0.875rem;
      }
      .line2 {
        background: #ececfe;
        width: 65%;
        height: 1rem;
      }
    }
  }
</style>
