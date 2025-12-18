<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { Address } from '$lib/address'
  import { type AddressFromBAN, callBAN } from '$lib/addressesFromBAN'
  import { buildAgenda } from '$lib/agenda'
  import { userStore } from '$lib/state/User.svelte'

  let addressFromUserStore: Address | undefined = $state()
  let timer: any
  let inputValue: string = $state('')
  let filteredAddresses: Address[] = $state([])
  let disabledButton: boolean = $state(true)
  let addressApiHasError: boolean = $state(false)
  let addressInputHasError: boolean = $state(false)
  let selectedAddress: Address | undefined = $state()
  let hasSelectedAddress: boolean = $state(false)
  let submittedAddress: Address | undefined = $state()

  onMount(async () => {
    if (!userStore.connected) {
      goto('/')
      return
    } else {
      addressFromUserStore = userStore.connected.identity.address
      if (addressFromUserStore) {
        hasSelectedAddress = true
        selectedAddress = addressFromUserStore
        submittedAddress = addressFromUserStore
      }
    }
  })

  const navigateToPreviousPage = async () => {
    window.history.back()
  }

  const addressInputHandler = (event: Event) => {
    if (!event.target) {
      return
    }
    const { value } = event.target as HTMLInputElement
    debounce(value)
  }

  const debounce = (value: string) => {
    clearTimeout(timer)
    timer = setTimeout(() => {
      inputValue = value
      filterAddresses()
    }, 750)
  }

  const filterAddresses = async () => {
    filteredAddresses = []
    if (inputValue) {
      try {
        const response = await callBAN(inputValue)
        addressApiHasError = response.errorCode === 'ban-unavailable'
        addressInputHasError = response.errorCode === 'ban-failed-parsing-query'
        if (!addressApiHasError && !addressInputHasError) {
          if (response.results) {
            filteredAddresses = response.results.map(
              (address: AddressFromBAN): Address => {
                const city = address.city
                const context = address.context
                const idBAN = address.id
                const label = address.label
                const name = address.name
                const postcode = address.postcode
                return new Address(city, context, idBAN, label, name, postcode)
              }
            )
          }
        }
      } catch (error) {
        console.error(error)
      }
    }
  }

  const setInputVal = (address: Address) => {
    selectedAddress = address
    filteredAddresses = []
    inputValue = selectedAddress.label

    const addressInput: HTMLInputElement | null =
      document.querySelector<HTMLInputElement>('#address-input')
    if (addressInput) {
      addressInput.focus()
    }

    hasSelectedAddress = true
    disabledButton = false
  }

  const cancelAddress = async () => {
    await navigateToPreviousPage()
  }

  const submitAddress = async () => {
    submittedAddress = selectedAddress
    if (userStore.connected) {
      userStore.connected.setAddress(selectedAddress)
      // rebuild agenda to create new scheduled notifications
      userStore.connected.clearScheduledNotificationCreatedKey()
      await buildAgenda()
    }
    console.log(submittedAddress)
    await navigateToPreviousPage()
  }

  const removeAddress = async () => {
    hasSelectedAddress = false
    if (userStore.connected) {
      userStore.connected.setAddress(undefined)
    }
    disabledButton = false
    selectedAddress = undefined
    submittedAddress = undefined
  }
</script>

<div class="address-form-page">
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
      <h2 class="fr-mb-0">Où habitez-vous&nbsp;?</h2>
    </div>
  </nav>

  <div class="address-content-container">
    <p>L'adresse de votre <strong>résidence principale</strong> permet de <strong>faciliter la communication</strong> avec les administrations.</p>

    <form autocomplete="on" class="address-form">
      <fieldset class="fr-fieldset" aria-labelledby="text-legend text-messages">
        <div class="fr-fieldset__element">
          <div class="fr-input-group autocomplete {addressInputHasError ? 'fr-input-group--error' : ''}">
            <label class="fr-label" for="address-input">
              Adresse
            </label>
            <span class="fr-hint-text">Par exemple&nbsp;: 23 rue des aubépines, Poitiers</span>
            <input class="fr-input"
                   id="address-input"
                   type="text"
                   bind:value={inputValue}
                   data-testid="address-input"
                   autocomplete="address-line1"
                   oninput={addressInputHandler}
            >
            {#if addressInputHasError}
              <div class="fr-messages-group" aria-live="polite">
                <p id="address-error" class="fr-message fr-message--error" data-testid="address-error">
                  Cette adresse est invalide. Conseil&nbsp;: saisissez entre 3 à 200 caractères et commencez par un nombre ou une lettre.
                </p>
              </div>
            {/if}
          </div>

          {#if filteredAddresses.length > 0}
            <ul id="autocomplete-items-list">
              <p class="autocomplete-title">
                Adresse
              </p>
              {#each filteredAddresses as address, index}
                <li class="autocomplete-item" data-testid="autocomplete-item-{index}">
                  <button type="button" onclick={() => setInputVal(address)} data-testid="autocomplete-item-button-{index}">
                    <p><strong>{address.name}</strong></p>
                    <p>{address.city} ({address.context})</p>
                  </button>
                </li>
              {/each}
            </ul>
          {/if}

        </div>
        <div class="fr-messages-group" id="text-messages" aria-live="polite">
        </div>
      </fieldset>
    </form>

    {#if addressApiHasError}
      <div class="fr-alert fr-alert--warning" data-testid="address-warning">
        <h3 class="fr-alert__title">Récupération de l'adresse indisponible</h3>
        <p>Notre outil est momentanément indisponible. Nous ne pouvons pas trouver votre adresse. Merci de réessayer plus tard.</p>
      </div>
    {/if}

    {#if hasSelectedAddress !== undefined && selectedAddress !== undefined}
      <div class="selected-address-wrapper" data-testid="selected-address-wrapper">
        <div class="left-wrapper">
          <span>Votre résidence principale</span>
          <span><strong>{selectedAddress.label}</strong></span>
        </div>
        <div class="right-wrapper">
          <button onclick={removeAddress} aria-label="Retirer l'adresse">
            <span class="fr-icon-close-line" aria-hidden="true"></span>
          </button>
        </div>
      </div>
    {/if}
  </div>

  <ul class="fr-btns-group action-buttons">
    <li>
      <button class="fr-btn fr-btn--secondary cancel-button"
              type="button"
              onclick={cancelAddress}
              data-testid="cancel-button"
      >
          Annuler
      </button>
    </li>
    <li>
      <button class="fr-btn submit-button"
              type="button"
              disabled="{disabledButton}"
              onclick={submitAddress}
              data-testid="submit-button"
      >
          Enregistrer
      </button>
    </li>
  </ul>
</div>

<style>
  .address-form-page {
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

    .address-content-container {
      padding: 1rem;

      .address-form {
        div.autocomplete {
          position: relative;
          display: inline-block;
          width: 100%;
          span.fr-hint-text {
            margin-bottom: .25rem;
          }
          input#address-input {
            padding: 1rem;
            font-size: 1rem;
            line-height: 1.5rem;
            margin: 0;
          }
        }

        .fr-input-group:not(:last-child) {
          margin-bottom: 0;
        }

        ul#autocomplete-items-list {
          position: relative;
          margin: 0;
          padding: 0;
          top: 0;
          border: 1px solid var(--grey-950-100);
          background-color: var(--grey-975-75);

          p.autocomplete-title {
            padding: .25rem .75rem;
            margin: 0;
            font-weight: 700;
            color: var(--text-active-blue-france);
          }

          li.autocomplete-item {
            list-style: none;
            padding: 0;
            background-color: var(--background-default-grey);

            button {
              padding: .75rem;
              width: 100%;
              text-align: left;
              --hover-tint: var(--text-action-high-blue-france);
              --active-tint: var(--text-action-high-blue-france);

              p {
                margin: 0;
              }
            }
          }

          li.autocomplete-item:hover {
            background-color: var(--text-action-high-blue-france);
            color: var(--text-inverted-blue-france);
          }
        }
      }
    }

    .selected-address-wrapper {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      border: 1px solid var(--text-action-high-blue-france);
      padding: 1rem .5rem 1rem 1.5rem;

      .left-wrapper {
        display: flex;
        flex-direction: column;
      }
      .right-wrapper {
        display: flex;
        align-items: center;
        .fr-icon-close-line {
          color: var(--text-action-high-blue-france);
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
