<script lang="ts">
import { callBAN } from './addressesFromBAN'

let timer
let inputValue = ''
let filteredAddresses = []
let disabledButton = true

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
    let results = []
    results = await callBAN(inputValue)
    filteredAddresses = results
  } else {
    filteredAddresses = []
  }
  console.log('filteredAddresses', filteredAddresses)
}

const setInputVal = (address) => {
  console.log('selected address', address)
  filteredAddresses = []
  document.querySelector('#address-input').focus()
  disabledButton = false
}
</script>

<nav class="fr-p-4v fr-pt-6v">
  <div class="back-link fr-mb-2v">
    <a href="/" title="Retour à la page d'accueil" aria-label="Retour à la page d'accueil">
      <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
    </a>
  </div>
  <div class="title">
    <h2 class="fr-mb-0">Quelle est votre adresse ?</h2>
  </div>
</nav>

<div class="address-content-container">
  <p>Pour <strong>personnaliser</strong> votre expérience, renseigner l'adresse de votre <strong>résidence principale.</p>

  <form autocomplete="off">
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
                 oninput={({ target: { value } }) => debounce(value)}
          >
        </div>

        {#if filteredAddresses.length > 0}
          <ul id="autocomplete-items-list">
            <p class="autocomplete-title">
              Adresse
            </p>
            {#each filteredAddresses as address}
              <li class="autocomplete-items"
                  onclick={() => setInputVal(address)}
              >
                <p><strong>{address.name}</strong></p>
                <p>{address.city} ({address.context})</p>
              </li>
            {/each}
          </ul>
        {/if}
      </div>
      <div class="fr-messages-group" id="text-messages" aria-live="polite">
      </div>
    </fieldset>

    <button class="fr-btn"
            type="submit"
            disabled="{disabledButton}"
    >
      Enregistrer cette adresse
    </button>
  </form>
</div>

<style>
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

      li.autocomplete-items {
        list-style: none;
        padding: .75rem;
        cursor: pointer;
        background-color: var(--background-default-grey);

        p {
          margin: 0;
        }
      }

      li.autocomplete-items:hover {
        background-color: var(--text-action-high-blue-france);
        color: var(--text-inverted-blue-france);
      }
    }
  }
</style>
