<script lang="ts">
import { type AddressFromBAN, callBAN } from './addressesFromBAN'

// TODO: essayer avec l'autocomplete

type Address = {
  city: string
  context: string
  idBAN: string
  label: string
  name: string
  postcode: string
}

let timer
let inputValue: string = $state('')
let filteredAddresses: [Address] = $state([])
let disabledButton: boolean = $state(true)
let selectedAddress: Address = $state<Address>({
  city: '',
  context: '',
  idBAN: '',
  label: '',
  name: '',
  postcode: '',
})
let hasSubmittedAddress: boolean = $state(false)
let submittedAddress: Address = $state<Address>({
  city: '',
  context: '',
  idBAN: '',
  label: '',
  name: '',
  postcode: '',
})

const debounce = (v) => {
  clearTimeout(timer)
  console.log('debounce')
  timer = setTimeout(() => {
    inputValue = v
    filterAddresses()
  }, 750)
}

const filterAddresses = async () => {
  if (inputValue) {
    let results: [AddressFromBAN] = []
    results = await callBAN(inputValue)
    filteredAddresses = results.map(
      (address: AddressFromBAN): Address => ({
        city: address.city,
        context: address.context,
        idBAN: address.id,
        label: address.label,
        name: address.name,
        postcode: address.postcode,
      })
    )
  } else {
    filteredAddresses = []
  }
  console.log('filteredAddresses', $state.snapshot(filteredAddresses))
}

const setInputVal = (address) => {
  selectedAddress = address
  console.log('selectedAddress', $state.snapshot(selectedAddress))
  filteredAddresses = []
  inputValue = selectedAddress.label
  document.querySelector('#address-input').focus()
  disabledButton = false
}

const submitAddress = async () => {
  hasSubmittedAddress = true
  submittedAddress = selectedAddress
  localStorage.setItem('user_address', JSON.stringify(submittedAddress))
  console.log('submittedAddress', $state.snapshot(submittedAddress))
}

const removeAddress = async () => {
  hasSubmittedAddress = false
  disabledButton = true
  selectedAddress = {
    city: '',
    context: '',
    idBAN: '',
    label: '',
    name: '',
    postcode: '',
  }
  submittedAddress = {
    city: '',
    context: '',
    idBAN: '',
    label: '',
    name: '',
    postcode: '',
  }
  localStorage.setItem('user_address', '')
  console.log('removeAddress')
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

    <form autocomplete="off" class="address-form">
      <fieldset class="fr-fieldset" aria-labelledby="text-legend text-messages">
        <div class="fr-fieldset__element">
          <div class="fr-input-group autocomplete">
            <label class="fr-label" for="address-input">
              Adresse
            </label>
            <span class="fr-hint-text">Par exemple : 23 rue des aubépines, Orléans</span>
            <input class="fr-input"
                   id="address-input"
                   type="text"
                   bind:value={inputValue}
                   data-testid="address-input"
                   oninput={({ target: { value } }) => debounce(value)}
            >
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
