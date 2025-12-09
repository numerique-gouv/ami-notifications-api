<script lang="ts">
import { type AddressFromBAN, callBAN } from './addressesFromBAN'
import { userStore } from '$lib/state/User.svelte'
import { Address } from '$lib/address'

let timer: any
let inputValue: string = $state('')
let filteredAddresses: Address[] = $state([])
let disabledButton: boolean = $state(true)
let addressHasError: boolean = $state(false)
let selectedAddress: Address = $state<Address>(new Address())
let hasSubmittedAddress: boolean = $state(false)
let submittedAddress: Address = $state<Address>(new Address())

const addressInputHandler = (event: Event) => {
  if (!event.target) return
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
      if (response.statusCode === 400) {
        addressHasError = true
      } else {
        addressHasError = false
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

  disabledButton = false
}

const submitAddress = async () => {
  hasSubmittedAddress = true
  submittedAddress = selectedAddress
  if (userStore.connected) {
    userStore.connected.address = selectedAddress
  }
  console.log(submittedAddress)
}

const removeAddress = async () => {
  hasSubmittedAddress = false
  delete userStore.connected?.identity?.address
  disabledButton = true
  selectedAddress = new Address()
  submittedAddress = new Address()
}
</script>

<div class="address-form-page">
  <nav class="fr-p-4v fr-pt-6v">
    <div class="back-link fr-mb-2v">
      <a href="/" title="Retour à la page d'accueil" aria-label="Retour à la page d'accueil">
        <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
      </a>
    </div>
    <div class="title">
      <h2 class="fr-mb-0">Quelle est votre adresse&nbsp;?</h2>
    </div>
  </nav>

  <div class="address-content-container">
    <p>Pour <strong>personnaliser</strong> votre expérience, renseigner l'adresse de votre <strong>résidence principale.</p>

    <form autocomplete="on" class="address-form">
      <fieldset class="fr-fieldset" aria-labelledby="text-legend text-messages">
        <div class="fr-fieldset__element">
          <div class="fr-input-group autocomplete {addressHasError ? 'fr-input-group--error' : ''}">
            <label class="fr-label" for="address-input">
              Adresse
            </label>
            <span class="fr-hint-text">Par exemple : 23 rue des aubépines, Orléans</span>
            <input class="fr-input"
                   id="address-input"
                   type="text"
                   bind:value={inputValue}
                   data-testid="address-input"
                   autocomplete="address-line1"
                   oninput={addressInputHandler}
            >
            {#if addressHasError}
              <div class="fr-messages-group" aria-live="polite">
                <p id="address-error" class="fr-message fr-message--error" data-testid="address-error">Merci d'indiquer une adresse valide. L'adresse doit contenir entre 3 et 200 caractères et commencer par un nombre ou une lettre.</p>
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
                  <button type="button" onclick={() => setInputVal(address)}  data-testid="autocomplete-item-button-{index}">
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

    {#if hasSubmittedAddress}
      <div class="selected-address-wrapper" data-testid="selected-address-wrapper">
        <div class="left-wrapper">
          <span>Votre résidence principale</span>
          <span><strong>{submittedAddress.label}</strong></span>
        </div>
        <div class="right-wrapper">
          <button onclick={removeAddress} aria-label="Retirer l'adresse">
            <span class="fr-icon-close-line" aria-hidden="true"></span>
          </button>
        </div>
      </div>
    {/if}
  </div>

  <button class="fr-btn submit-button"
          type="submit"
          disabled="{disabledButton}"
          onclick={submitAddress}
          data-testid="submit-button"
  >
    Enregistrer cette adresse
  </button>
</div>

<style>
  .address-form-page {
    nav {
      .back-link {
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
      padding: .5rem;

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

    .submit-button {
      position: fixed;
      bottom: 1.5rem;
      left: 50%;
      transform: translateX(-50%);

      display: block;
      width: 328px;
    }
  }
</style>
