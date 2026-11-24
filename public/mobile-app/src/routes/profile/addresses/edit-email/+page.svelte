<script lang="ts">
  import { onMount } from 'svelte';
  import { isEmail } from 'validator';
  import { AMIBack, AMIGoto } from '$lib/ami-navigation';
  import Banner from '$lib/components/Banner.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import PageWrapper from '$lib/components/PageWrapper.svelte';
  import { toastStore } from '$lib/state/toast.svelte';
  import type { DataOrigin } from '$lib/state/User.svelte';
  import { userStore } from '$lib/state/User.svelte';
  import { formatShortDate, scrollToInput, scrollToLabel } from '$lib/utils';

  let backUrl: string = '/#/profile';
  let inputValue: string = $state('');
  let email_origin: DataOrigin | undefined = $state();
  let email_last_update: Date | undefined = $state();
  let emailInputHasError: boolean = $state(false);

  onMount(() => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    } else {
      const identity = userStore.connected.identity;
      const currentValue = identity.email;
      inputValue = currentValue || '';
      email_origin = identity.dataDetails.email.origin;
      email_last_update = identity.dataDetails.email.lastUpdate;
    }
  });

  const cancel = () => {
    AMIBack(backUrl);
  };

  const submit = () => {
    if (userStore.connected && inputValue) {
      if (isEmail(inputValue)) {
        userStore.connected.setEmail(inputValue);
        console.log('Updated the email to', inputValue);
        toastStore.addToast('Information bien enregistrée !', 'success', 3000, false);
      } else {
        emailInputHasError = true;
        return;
      }
    }
    AMIBack(backUrl);
  };
</script>

<PageWrapper>
  {#snippet header()}
    <NavWithBackButton className="small-header" title="Contact" {backUrl} />
  {/snippet}

  {#snippet content()}
    <div class="content-container" data-testid="container">
      <p class="fr-mb-2w">Vous pouvez modifier uniquement les champs ci-dessous.</p>

      <form autocomplete="on" novalidate onsubmit={submit}>
        <fieldset class="fr-fieldset fr-mb-3w">
          <div class="fr-fieldset__element fr-mb-0">
            <div
              class="fr-input-group autocomplete {emailInputHasError ? 'fr-input-group--error' : ''}"
            >
              <label class="fr-label" for="input">
                E-mail
                <span class="fr-hint-text">Par exemple&nbsp;: michel@dupont.com</span>
              </label>
              <input
                class="fr-input"
                id="input"
                type="email"
                bind:value={inputValue}
                data-testid="email-input"
                autocomplete="email"
                onfocus={scrollToLabel}
                aria-describedby="email-error-message last-modif-email"
              >
              <div
                class="fr-messages-group"
                id="email-error-message"
                aria-live="polite"
              >
                {#if emailInputHasError}
                  <p
                    id="email-error"
                    class="fr-message fr-message--error"
                    data-testid="email-error"
                  >
                    Le format de l’adresse electronique saisie n’est pas valide
                    (exemple&nbsp;: michel.dupont@example.com)
                  </p>
                {/if}
              </div>
            </div>
          </div>
        </fieldset>
      </form>

      {#if email_origin == 'user' && email_last_update}
        <div class="fr-hint-text data-update-info fr-mb-3w" id="last-modif-email">
          Vous avez modifié cette information le
          {formatShortDate(email_last_update)}.
        </div>
      {/if}

      <Banner
        id="edit-email-change-not-submitted-info"
        title="Modification non transmise"
        description="La modification de la donnée ne sera pas transmise aux différentes administrations."
        bannerType="info"
      />
    </div>
  {/snippet}

  {#snippet footer()}
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
  {/snippet}
</PageWrapper>

<style>
  .action-buttons {
    background-color: var(--background-default-grey);
    display: flex;
    gap: 1rem;
    margin: 0;

    li {
      flex: 1;

      button {
        display: block;
        width: 100%;
        margin: 0;
      }
    }
  }
</style>
