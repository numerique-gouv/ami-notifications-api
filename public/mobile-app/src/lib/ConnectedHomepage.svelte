<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { type Agenda, Item as AgendaItemType, buildAgenda } from '$lib/agenda';
  import AgendaItem from '$lib/components/AgendaItem.svelte';
  import FollowupItem from '$lib/components/FollowupItem.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import AgendaItemModal from '$lib/components/modal/AgendaItemModal.svelte';
  import FollowupItemModal from '$lib/components/modal/FollowupItemModal.svelte';
  import Logout from '$lib/components/modal/Logout.svelte';
  import Modal from '$lib/components/modal/Modal.svelte';
  import type { Followup, FollowupItem as FollowupItemType } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import { userReady } from '$lib/initializeDataFromAPI';
  import {
    countUnreadNotifications,
    notificationEventsSocket,
  } from '$lib/notifications';
  import { userStore } from '$lib/state/User.svelte';

  type ModalInstance = {
    open: () => Promise<void>;
  };

  let logoutModal: ModalInstance;

  let unreadNotificationsCount: number = $state(0);
  let initials: string = $state('');
  let isMenuDisplayed: boolean = $state(false);
  let isAgendaEmpty: boolean = $state(true);
  let agenda: Agenda | null = $state(null);
  let isFollowupEmpty: boolean = $state(true);
  let followup: Followup | null = $state(null);
  let selectedAgendaItem: AgendaItemType | null = $state(null);
  let selectedFollowupItem: FollowupItemType | null = $state(null);

  onMount(async () => {
    console.log('User is connected:', userStore.connected);
    try {
      initials = userStore.connected?.getInitials() || '';

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

      await userReady;
      agenda = await buildAgenda();
      console.log($state.snapshot(agenda));
      isAgendaEmpty = !(agenda.now.length || agenda.next.length);
      followup = await buildFollowup();
      console.log($state.snapshot(followup));
      isFollowupEmpty = !followup.items.length;
    } catch (error) {
      console.error(error);
    }
  });

  const toggleMenu = () => {
    isMenuDisplayed = !isMenuDisplayed;
  };

  const goToProfile = async () => {
    goto('/#/profile');
  };

  const goToPreferences = () => {
    goto('/#/preferences');
  };

  const goToContact = () => {
    goto('/#/contact');
  };

  const openLogoutModal = () => {
    isMenuDisplayed = false;
    logoutModal.open();
  };

  const openAgendaItemModal = (item: AgendaItemType) => {
    selectedAgendaItem = item;
  };

  const openFollowupItemModal = (item: FollowupItemType) => {
    selectedFollowupItem = item;
  };
</script>

<div class="homepage-connected">
  <div class="header fr-mb-3w">
    <button class="header-left" onclick={toggleMenu} data-testid="toggle-menu-button">
      <span class="user-profile"> {initials} </span>
    </button>

    <div class="header-right">
      <div class="notification-svg-icon" id="notification-icon">
        <a
          aria-label="Voir les notifications({unreadNotificationsCount})"
          href="/#/notifications"
        >
          <img src="/remixicons/notification-3.svg" alt="">
          <div class="count-number-wrapper" data-content="{unreadNotificationsCount}">
            {unreadNotificationsCount}
          </div>
        </a>
      </div>
    </div>
  </div>

  <div class="menu {isMenuDisplayed ? '' : 'is-hidden'}">
    <div class="container">
      <button
        class="profile"
        type="button"
        onclick={goToProfile}
        data-testid="profile-button"
      >
        <Icon
          className="fr-mr-2v"
          color="var(--text-active-blue-france)"
          href="/remixicons/user-line.svg"
        />
        Mon profil
      </button>

      <button
        class="preferences"
        type="button"
        onclick={goToPreferences}
        data-testid="preferences-button"
      >
        <Icon
          className="fr-mr-2v"
          color="var(--text-active-blue-france)"
          href="/remixicons/settings.svg"
        />
        Préférences
      </button>

      <button
        class="contact"
        type="button"
        onclick={goToContact}
        data-testid="contact-button"
      >
        <Icon
          className="fr-mr-2v"
          color="var(--text-active-blue-france)"
          href="/remixicons/question-answer-line.svg"
        />
        Nous contacter
      </button>

      <button class="fr-connect-logout" type="button" onclick={openLogoutModal}>
        <Icon
          className="fr-mr-2v"
          color="var(--text-active-blue-france)"
          href="/remixicons/shut-down-line.svg"
        />
        Me déconnecter
      </button>
    </div>
  </div>

  {#if !userStore.connected?.identity?.address}
    <div class="rubrique-container address-container">
      <div class="rubrique-content-container">
        <div
          class="fr-tile fr-tile-sm fr-tile--horizontal fr-tile--no-border fr-enlarge-link"
        >
          <div class="fr-tile__body">
            <div class="fr-tile__content">
              <img class="address-icon" src="/remixicons/house.svg" alt="">
              <h3 class="fr-tile__title">
                <a href="/#/edit-address"
                  ><b
                    >Renseignez votre adresse sur l'application pour faciliter vos
                    échanges&nbsp;!</b
                  ></a
                >
              </h3>
            </div>
          </div>
        </div>
      </div>
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
            <img class="address-icon" src="/remixicons/calendar.svg" alt="">
          </div>
          <div class="no-agenda--title">
            Retrouvez les temps importants de votre vie administrative ici
          </div>
        </div>
      </div>
    {:else}
      <div class="header-container fr-mb-1w">
        <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mon agenda</h2>
        <a class="see-all" aria-label="Voir tous mes évènements" href="/#/agenda">
          <span>Voir tout</span>
          <img class="arrow-line" src="/remixicons/arrow-line.svg" alt="">
        </a>
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

  <div class="rubrique-container followup-container">
    {#if isFollowupEmpty}
      <div class="header-container fr-mb-1w">
        <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mes démarches</h2>
      </div>
      <div class="rubrique-content-container">
        <div class="no-followup rubrique-content-container--empty">
          <div class="no-followup--icon">
            <img class="address-icon" src="/remixicons/tracking.svg" alt="">
          </div>
          <div class="no-followup--title">Retrouvez et suivez vos démarches ici.</div>
        </div>
      </div>
    {:else}
      <div class="header-container fr-mb-1w">
        <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mes démarches</h2>
        <a class="see-all" aria-label="Voir toutes mes démarches" href="/#/followup">
          <span>Voir tout</span>
          <img class="arrow-line" src="/remixicons/arrow-line.svg" alt="">
        </a>
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
</div>

<Modal
  bind:this={logoutModal}
  id="modal-logout"
  title="Suppression de vos données"
  closeButton={false}
  centered={true}
  component={Logout}
/>

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

<style>
  .is-hidden {
    display: none;
  }

  .homepage-connected {
    padding: 1.5rem 1rem;
    margin-bottom: 68px;

    .header {
      display: flex;
      justify-content: space-between;

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

          & a[href] {
            background: none;
          }

          .count-number-wrapper {
            position: absolute;
            top: 0;
            left: 0.75rem;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 18px;
            height: 18px;
            border-radius: 0.5rem;
            background-color: #e1000f;
            color: white;
            font-size: 10px;
            font-weight: 700;

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
          align-items: center;
          display: flex;
          flex-direction: row;
          padding: 8px 12px;

          font-size: 14px;
          line-height: 24px;
        }
      }
    }

    .rubrique-container {
      &:not(:last-child) {
        margin-bottom: 24px;
      }

      .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .see-all {
          font-size: 14px;
          font-weight: 400;
          line-height: 24px;
          color: var(--blue-france-sun-113-625);
          margin-right: 4px;
          display: inline-flex;
          gap: 4px;
        }
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
  }
</style>
