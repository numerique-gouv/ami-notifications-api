<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { type Agenda, Item as AgendaItemType, buildAgenda } from '$lib/agenda';
  import { AutoPromo, buildAutoPromo } from '$lib/auto-promo';
  import AgendaItem from '$lib/components/AgendaItem.svelte';
  import AutoPromoItem from '$lib/components/AutoPromoItem.svelte';
  import FollowupItem from '$lib/components/FollowupItem.svelte';
  import AgendaItemModal from '$lib/components/modal/AgendaItemModal.svelte';
  import CenteredModal from '$lib/components/modal/CenteredModal.svelte';
  import FollowupItemModal from '$lib/components/modal/FollowupItemModal.svelte';
  import type { Followup, FollowupItem as FollowupItemType } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import {
    countUnreadNotifications,
    notificationEventsSocket,
  } from '$lib/notifications';
  import { userStore } from '$lib/state/User.svelte';
  import { formatDate } from '$lib/utils';

  let unreadNotificationsCount: number = $state(0);
  let firstName: string = $state('');
  let today: Date | null = $state(null);
  let isAgendaEmpty: boolean = $state(true);
  let agenda: Agenda | null = $state(null);
  let isFollowupEmpty: boolean = $state(true);
  let followup: Followup | null = $state(null);
  let selectedAgendaItem: AgendaItemType | null = $state(null);
  let selectedFollowupItem: FollowupItemType | null = $state(null);
  let autoPromo: AutoPromo | null = $state(null);
  const has_consented = userStore.connected?.hasConsented();

  onMount(async () => {
    console.log('User is connected:', userStore.connected);
    try {
      firstName = userStore.connected?.getFirstName() || '';
      today = new Date();

      unreadNotificationsCount = await countUnreadNotifications();

      const onMessage = async () => {
        console.log(
          'New message received from the websocket, counting unread notifications'
        );
        unreadNotificationsCount = await countUnreadNotifications();
      };
      let ws = notificationEventsSocket(onMessage);

      const handleVisibility = async () => {
        if (
          document.visibilityState === 'visible' &&
          ws.readyState !== WebSocket.OPEN
        ) {
          console.log('Reconnecting the websocket');
          ws = notificationEventsSocket(onMessage);
          unreadNotificationsCount = await countUnreadNotifications();
        }
      };
      document.addEventListener('visibilitychange', handleVisibility);

      agenda = await buildAgenda();
      console.log($state.snapshot(agenda));
      isAgendaEmpty = !(agenda.now.length || agenda.next.length);
      autoPromo = buildAutoPromo(agenda);
      followup = await buildFollowup();
      console.log($state.snapshot(followup));
      isFollowupEmpty = !followup.items.length;
    } catch (error) {
      console.error(error);
    }
  });

  const openAgendaItemModal = (item: AgendaItemType) => {
    selectedAgendaItem = item;
  };

  const openFollowupItemModal = (item: FollowupItemType) => {
    selectedFollowupItem = item;
  };

  const gotoConsents = () => {
    goto('/#/consents');
  };
</script>

<div class="fr-container fr-py-3w fr-mb-17v homepage-connected">
  <div class="header fr-mb-3w">
    <div class="header-left fr-ellipsis">
      <p class="fr-ellipsis fr-h5 fr-mb-1w">Bonjour {firstName}</p>
      <p class="fr-text--sm fr-mb-0">{today ? formatDate(today): ''}</p>
    </div>

    <div class="header-right">
      <div class="notification-svg-icon" id="notification-icon">
        <button
          type="button"
          class="fr-btn fr-icon-notification-3-line fr-btn--tertiary-no-outline"
          onclick={() => goto("/#/notifications")}
        >
          Voir les notifications({unreadNotificationsCount})
          <div
            class="fr-text--bold count-number-wrapper"
            data-content="{unreadNotificationsCount}"
          >
            {unreadNotificationsCount}
          </div>
        </button>
      </div>
    </div>
  </div>

  {#if autoPromo && autoPromo.items.length}
    {@const firstItem = autoPromo.items[0]}
    <div class="rubrique-container">
      <AutoPromoItem item={firstItem} />
    </div>
  {/if}

  <div class="rubrique-container agenda-container">
    {#if isAgendaEmpty}
      <div class="header-container fr-mb-1w">
        <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mon agenda</h2>
      </div>
      <div class="rubrique-content-container">
        <div class="no-agenda rubrique-content-container--empty">
          <div class="no-agenda--icon">
            <img src="/remixicons/calendar.svg" alt="">
          </div>
          <div class="no-agenda--title">
            Retrouvez les temps importants de votre vie administrative ici
          </div>
        </div>
      </div>
    {:else}
      <div class="header-container fr-mb-1w">
        <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mon agenda</h2>
        <button
          type="button"
          class="fr-link fr-icon-arrow-right-line fr-link--icon-right am-link-icon-xl"
          aria-label="Voir tous mes évènements"
          onclick={() => goto("/#/agenda")}
        ></button>
      </div>
      <div class="rubrique-content-container">
        {#if agenda && agenda.now.length}
          {@const firstItem = agenda.now[0]}
          <AgendaItem
            item={firstItem}
            onOpen={() => openAgendaItemModal(firstItem)}
            displayDate={false}
          />
        {:else if agenda && agenda.next.length}
          {@const firstItem = agenda.next[0]}
          <AgendaItem
            item={firstItem}
            onOpen={() => openAgendaItemModal(firstItem)}
            displayDate={false}
          />
        {/if}
      </div>
    {/if}
  </div>

  {#if has_consented}
    <div class="rubrique-container followup-container">
      {#if isFollowupEmpty}
        <div class="header-container fr-mb-1w">
          <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mes démarches</h2>
        </div>
        <div class="rubrique-content-container">
          <div class="no-followup rubrique-content-container--empty">
            <div class="no-followup--icon">
              <img src="/remixicons/tracking.svg" alt="">
            </div>
            <div class="no-followup--title">Suivez vos démarches ici.</div>
          </div>
        </div>
      {:else}
        <div class="header-container fr-mb-1w">
          <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mes démarches</h2>
          <button
            type="button"
            class="fr-link fr-icon-arrow-right-line fr-link--icon-right am-link-icon-xl"
            aria-label="Voir toutes mes démarches"
            onclick={() => goto("/#/followup")}
          ></button>
        </div>
        <div class="rubrique-content-container">
          {#if followup && followup.items.length}
            {@const firstItem = followup.items[0]}
            <FollowupItem
              item={firstItem}
              onOpen={() => openFollowupItemModal(firstItem)}
            />
          {/if}
        </div>
      {/if}
    </div>
  {:else}
    <div class="rubrique-container followup-container">
      <div class="header-container fr-mb-1w">
        <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mes démarches</h2>
        <button
          type="button"
          class="fr-link fr-icon-arrow-right-line fr-link--icon-right fr-text--sm am-link-bordered"
          aria-label="Voir toutes mes démarches"
          onclick={() => goto("/#/followup")}
        >
          Voir tout
        </button>
      </div>
      <div class="rubrique-content-container">
        <div class="fr-pt-2v">
          <p class="fr-mb-4v">
            Suivez vos démarches administratives au même endroit&nbsp;!
          </p>
          <div class="consent-action-button">
            <button
              class="fr-btn fr-btn--lg"
              type="button"
              onclick={gotoConsents}
              data-testid="consent-button"
            >
              Je veux suivre mes démarches
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

{#if selectedAgendaItem}
  <AgendaItemModal bind:item={selectedAgendaItem} bind:agenda={agenda} />
{/if}

{#if selectedFollowupItem}
  <FollowupItemModal
    bind:item={selectedFollowupItem}
    bind:followup={followup}
    bind:isFollowupEmpty={isFollowupEmpty}
  />
{/if}

<style lang="scss">
  .homepage-connected {
    .header {
      display: flex;
      justify-content: space-between;
      &-left {
        max-width: calc(100% - 3.5rem);
      }
      &-right {
        display: flex;
        .notification-svg-icon {
          position: relative;
          .count-number-wrapper {
            position: absolute;
            display: flex;
            justify-content: center;
            align-items: center;
            top: .125rem;
            right: .125rem;
            width: 1.125rem;
            height: 1.125rem;
            border-radius: 1.125rem;
            background-color: var(--red-marianne-main-472);
            color: var(--grey-1000-50);
            font-size: 10px;
            &[data-content="0"] {
              display: none;
            }
          }
        }
      }
    }

    .rubrique-container {
      &:not(:last-child) {
        margin-bottom: 1.5rem;
      }
      .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .rubrique-content-container--empty {
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

    .followup-container {
      .consent-action-button {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        button {
          display: flex;
          justify-content: center;
          width: 100%;
        }
      }
    }
  }
</style>
