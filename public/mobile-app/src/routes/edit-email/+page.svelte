<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import type { DataOrigin } from '$lib/state/User.svelte'
  import { userStore } from '$lib/state/User.svelte'
  import { formatDate } from '$lib/utils'

  let inputValue: string = $state('')
  let email_origin: DataOrigin | undefined = $state()
  let email_last_update: Date | undefined = $state()

  onMount(() => {
    if (!userStore.connected) {
      goto('/')
      return
    } else {
      const identity = userStore.connected.identity
      const currentValue = identity.email
      inputValue = currentValue || ''
      email_origin = identity.dataDetails.email.origin
      email_last_update = identity.dataDetails.email.lastUpdate
    }
  })

  const navigateToPreviousPage = async () => {
    window.history.back()
  }

  const cancel = async () => {
    await navigateToPreviousPage()
  }

  const submit = async () => {
    if (userStore.connected && inputValue) {
      userStore.connected.setEmail(inputValue)
      console.log('Updated the email to', inputValue)
    }
    await navigateToPreviousPage()
  }
</script>

<div class="form-page">
  <nav class="fr-p-4v fr-pt-6v">
    <div class="back-link fr-mb-2v">
      <button
        onclick={navigateToPreviousPage}
        title="Retour à la page d'accueil"
        aria-label="Retour à la page d'accueil"
      >
        <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
      </button>
    </div>
    <div class="title">
      <h2 class="fr-mb-0">Contact</h2>
    </div>
  </nav>

  <div class="content-container" data-testid="container">
    <p>Vous pouvez modifier uniquement les champs ci-dessous.</p>

    <form autocomplete="on">
      <fieldset class="fr-fieldset" aria-labelledby="text-messages">
        <div class="fr-fieldset__element">
          <div class="fr-input-group autocomplete">
            <label class="fr-label" for="input">Email</label>
            <span class="fr-hint-text">Par exemple&nbsp;: michel@dupont.com</span>
            <input
              class="fr-input"
              id="input"
              type="text"
              bind:value={inputValue}
              data-testid="email-input"
              autocomplete="email"
            >
          </div>
        </div>
        <div
          class="fr-messages-group data-update-info"
          id="text-messages"
          aria-live="polite"
        >
          {#if email_origin == 'user' && email_last_update}
            Vous avez modifié cette information le
            {formatDate(email_last_update)}.
          {/if}
        </div>
      </fieldset>
    </form>
  </div>

  <ul class="fr-btns-group action-buttons">
    <li>
      <button
        class="fr-btn fr-btn--secondary cancel-button"
        type="button"
        onclick={cancel}
        data-testid="cancel-button"
      >
        Annuler
      </button>
    </li>
    <li>
      <button
        class="fr-btn submit-button"
        type="button"
        disabled="{!inputValue}"
        onclick={submit}
        data-testid="submit-button"
      >
        Enregistrer
      </button>
    </li>
  </ul>
</div>

<style>
  .form-page {
    nav {
      .back-link {
        color: var(--text-active-blue-france);
        button {
          padding: 0;
        }
      }
      .title {
        display: flex;
        h2 {
          flex-grow: 1;
        }
      }
    }

    .content-container {
      padding: 1rem;

      form {
        div.autocomplete {
          position: relative;
          display: inline-block;
          width: 100%;
          span.fr-hint-text {
            margin-bottom: 0.25rem;
          }
          #input {
            max-height: 3.25rem;
            padding: 1rem;
            font-size: 1rem;
            line-height: 1.5rem;
            margin: 0;
          }
        }
        .data-update-info {
          font-size: 0.75rem;
          line-height: 1.25rem;
          color: var(--text-mention-grey);
        }
      }
    }

    .action-buttons {
      position: fixed;
      bottom: 0;
      z-index: 1;
      background-color: var(--background-default-grey);
      display: flex;
      gap: 1rem;
      width: 100%;
      margin: 0;
      padding: 1rem;

      li {
        flex: 1;

        button {
          display: block;
          width: 100%;
          margin: 0;
        }
      }
    }
  }
</style>
