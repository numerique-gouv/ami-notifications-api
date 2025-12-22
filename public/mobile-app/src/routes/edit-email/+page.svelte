<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { Address } from '$lib/address'
  import { type AddressFromBAN, callBAN } from '$lib/addressesFromBAN'
  import { buildAgenda } from '$lib/agenda'
  import { userStore } from '$lib/state/User.svelte'

  let inputValue: string = $state('')
  let disabledButton: boolean = $state(true)

  onMount(async () => {
    if (!userStore.connected) {
      goto('/')
      return
    } else {
      const currentValue = userStore.connected.identity.email
      inputValue = currentValue || ''
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
      <button onclick={navigateToPreviousPage}
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

  <div class="content-container">
    <p>Vous pouvez modifier uniquement les champs ci-dessous.</p>

    <form autocomplete="on">
      <fieldset class="fr-fieldset">
        <div class="fr-fieldset__element">
          <div class="fr-input-group autocomplete">
            <label class="fr-label" for="input">
              Email
            </label>
            <span class="fr-hint-text">Par exemple&nbsp;: michel@dupont.com</span>
            <input class="fr-input"
                   id="input"
                   type="text"
                   bind:value={inputValue}
                   data-testid="email-input"
                   autocomplete="email"
            >
          </div>
        </div>
      </fieldset>
    </form>
  </div>

  <ul class="fr-btns-group action-buttons">
    <li>
      <button class="fr-btn fr-btn--secondary cancel-button"
              type="button"
              onclick={cancel}
              data-testid="cancel-button"
      >
          Annuler
      </button>
    </li>
    <li>
      <button class="fr-btn submit-button"
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
            margin-bottom: .25rem;
          }
          #input {
            padding: 1rem;
            font-size: 1rem;
            line-height: 1.5rem;
            margin: 0;
          }
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

