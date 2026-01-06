<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import AgendaItem from '$lib/AgendaItem.svelte'
  import type { Agenda } from '$lib/agenda'
  import { buildAgenda } from '$lib/agenda'
  import { getQuotientData } from '$lib/api-particulier'
  import Icon from '$lib/components/Icon.svelte'
  import {
    countUnreadNotifications,
    notificationEventsSocket,
  } from '$lib/notifications'
  import { userStore } from '$lib/state/User.svelte'

  let quotientinfo: object = $state({})
  let unreadNotificationsCount: number = $state(0)
  let initials: string = $state('')
  let isMenuDisplayed: boolean = $state(false)
  let isAgendaEmpty: boolean = $state(true)
  let agenda: Agenda | null = $state(null)

  onMount(async () => {
    console.log('User is connected:', userStore.connected)
    try {
      initials = userStore.connected?.getInitials() || ''

      unreadNotificationsCount = await countUnreadNotifications()
      notificationEventsSocket(async () => {
        unreadNotificationsCount = await countUnreadNotifications()
      })

      agenda = await buildAgenda()
      console.log($state.snapshot(agenda))
      isAgendaEmpty = !(agenda.now.length || agenda.next.length)

      quotientinfo = await getQuotientData()
      console.log($state.snapshot(quotientinfo))
    } catch (error) {
      console.error(error)
    }
  })

  const toggleMenu = () => {
    isMenuDisplayed = !isMenuDisplayed
  }

  const goToProfile = async () => {
    goto('/#/profile')
  }

  const goToSettings = () => {
    goto('/#/settings')
  }

  const goToContact = () => {
    goto('/#/contact')
  }
</script>

<div class="homepage-connected">
  <div class="header">
    <button class="header-left" onclick={toggleMenu} data-testid="toggle-menu-button">
      <span class="user-profile"> {initials} </span>
    </button>

    <div class="header-right">
      <div class="notification-svg-icon" id="notification-icon">
        <a href="/#/notifications">
          <img src="/remixicons/notification-3.svg" alt="Icône de notifications">
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
        class="settings"
        type="button"
        onclick={goToSettings}
        data-testid="settings-button"
      >
        <Icon
          className="fr-mr-2v"
          color="var(--text-active-blue-france)"
          href="/remixicons/settings.svg"
        />
        Paramètres
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

      <button class="fr-connect-logout" type="button" onclick={userStore.logout}>
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
              <img class="address-icon" src="/remixicons/house.svg" alt="Icône adresse">
              <h3 class="fr-tile__title">
                <a href="/#/edit-address"
                  ><b
                    >Renseignez votre adresse sur l'application pour faciliter vos
                    échanges !</b
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
      <div class="header-container"><span class="title">Mon agenda</span></div>
      <div class="rubrique-content-container">
        <div class="no-agenda rubrique-content-container--empty">
          <div class="no-agenda--icon">
            <img
              class="address-icon"
              src="/remixicons/calendar.svg"
              alt="Icône d'agenda"
            >
          </div>
          <div class="no-agenda--title">
            Retrouvez les temps importants de votre vie administrative ici
          </div>
        </div>
      </div>
    {:else}
      <div class="header-container">
        <span class="title">Mon agenda</span>
        <a class="see-all" title="Voir tous mes évènements" href="/#/agenda">
          <span>Voir tout</span>
          <img
            class="arrow-line"
            src="/remixicons/arrow-line.svg"
            alt="Icône de flèche"
          >
        </a>
      </div>
      <div class="rubrique-content-container">
        {#if agenda?.now.length}
          <AgendaItem item={agenda.now[0]} displayDate={false} />
        {:else if agenda?.next.length}
          <AgendaItem item={agenda.next[0]} displayDate={false} />
        {/if}
      </div>
    {/if}
  </div>

  <div class="rubrique-container requests-container">
    <div class="header-container"><span class="title">Mes demandes</span></div>
    <div class="rubrique-content-container">
      <div class="no-requests rubrique-content-container--empty">
        <div class="no-requests--icon">
          <img class="address-icon" src="/remixicons/tracking.svg" alt="Icône de suivi">
        </div>
        <div class="no-requests--title">Suivez toutes vos démarches ici.</div>
      </div>
    </div>
  </div>
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
  }
</style>
