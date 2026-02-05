<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte'
  import type { DataOrigin } from '$lib/state/User.svelte'
  import { userStore } from '$lib/state/User.svelte'
  import { formatDate } from '$lib/utils'

  let backUrl: string = '/#/profile'
  let inputValue: string = $state('')
  let preferred_username_origin: DataOrigin | undefined = $state()
  let preferred_username_last_update: Date | undefined = $state()

  onMount(() => {
    if (!userStore.connected) {
      goto('/')
      return
    } else {
      const identity = userStore.connected.identity
      const currentValue = identity.preferred_username
      inputValue = currentValue || ''
      preferred_username_origin = identity.dataDetails.preferred_username.origin
      preferred_username_last_update =
        identity.dataDetails.preferred_username.lastUpdate
    }
  })

  const navigateToPreviousPage = async () => {
    goto(backUrl)
  }

  const cancel = async () => {
    await navigateToPreviousPage()
  }

  const submit = async () => {
    if (userStore.connected) {
      userStore.connected.setPreferredUsername(inputValue)
      console.log('Updated the preferred username to', inputValue)
    }
    await navigateToPreviousPage()
  }
</script>

<div class="form-page">
  <NavWithBackButton title="Mon identité" {backUrl} />

  <div class="content-container" data-testid="container">
    <p>Vous pouvez modifier uniquement les champs ci-dessous.</p>

    <form autocomplete="on">
      <fieldset class="fr-fieldset">
        <div class="fr-fieldset__element">
          <div class="fr-input-group autocomplete">
            <label class="fr-label" for="input">Nom d'usage</label>
            <span class="fr-hint-text">Par exemple&nbsp;: Dupont</span>
            <input
              class="fr-input"
              id="input"
              type="text"
              bind:value={inputValue}
              data-testid="preferred-username-input"
              autocomplete="username"
            >
          </div>
        </div>
      </fieldset>
    </form>
    {#if preferred_username_origin == 'user' && preferred_username_last_update}
      <div class="data-update-info">
        Vous avez modifié cette information le
        {formatDate(preferred_username_last_update)}.
      </div>
    {/if}
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
        .fr-fieldset {
          margin-bottom: 0.5rem;
        }
      }
      .data-update-info {
        font-size: 0.75rem;
        line-height: 1.25rem;
        color: var(--text-mention-grey);
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
