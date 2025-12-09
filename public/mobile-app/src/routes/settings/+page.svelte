<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { disableNotifications, enableNotifications } from '$lib/notifications'
  import type { Registration } from '$lib/registration'
  import { userStore } from '$lib/state/User.svelte'

  let registration: Registration | null = $state(null)
  let isChecked = $state(false)
  let disabledButton: boolean = $state(true)

  onMount(async () => {
    if (!userStore.connected) {
      goto('/')
    }

    isChecked = localStorage.getItem('notifications_enabled') === 'true'
  })

  const enableButton = async () => {
    disabledButton = false
  }

  const saveSettings = async () => {
    if (isChecked) {
      registration = await enableNotifications()
      if (registration) {
        localStorage.setItem('registration_id', registration.id)
        localStorage.setItem('notifications_enabled', 'true')
      }
    } else {
      let registrationId: string | null = null
      if (registration) {
        registrationId = registration.id
      } else if (localStorage.getItem('registration_id')) {
        registrationId = localStorage.getItem('registration_id')
      } else {
        console.log('no registration')
      }

      if (registrationId) {
        await disableNotifications(registrationId)
        localStorage.setItem('registration_id', '')
        localStorage.setItem('notifications_enabled', 'false')
      }
    }
  }
</script>

<div class="settings-page">
  <nav>
    <div class="back-link">
      <a href="/" title="Retour à la page d'accueil" aria-label="Retour à la page d'accueil">
        <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
      </a>
    </div>
    <div class="title">
      <h2>Paramètres</h2>
    </div>
  </nav>

  <div class="settings-content-container">
    <div class="fr-toggle">
      <input type="checkbox"
             class="fr-toggle__input"
             id="toggle"
             aria-describedby="toggle-messages toggle-hint"
             bind:checked={isChecked}
             onchange={enableButton}
             data-testid="toggle-input"
      >
      <label class="fr-toggle__label" for="toggle">
        Recevoir les notifications sur mon appareil mobile
      </label>
    </div>
  </div>

  <button class="fr-btn save-settings-button"
          type="button"
          disabled="{disabledButton}"
          onclick={saveSettings}
          data-testid="save-settings-button"
  >
    Enregistrer mes préférences
  </button>
</div>

<style>
  .settings-page {
    nav {
      padding: 1.5rem 1rem;
      .back-link {
        margin-bottom: .5rem;
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
          margin-bottom: 0;
        }
      }
    }

    .settings-content-container {
      padding: 1rem;

      .fr-toggle {
        .fr-toggle__label {
          display: flex;
          position: relative;
          &:before {
            display: flex;
            position: absolute;
            right: 0;
            margin: 0;
          }
          &:after {
            position: absolute;
            left: auto !important;
            right: 1rem !important;
          }
        }
      }
    }

    .save-settings-button {
      position: fixed;
      bottom: 1rem;
      left: 50%;
      transform: translateX(-50%);

      display: block;
      width: 328px;
    }
  }
</style>
