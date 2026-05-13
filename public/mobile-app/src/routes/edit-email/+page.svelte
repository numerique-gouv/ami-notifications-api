<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import PageWrapper from '$lib/components/PageWrapper.svelte';
  import { toastStore } from '$lib/state/toast.svelte';
  import type { DataOrigin } from '$lib/state/User.svelte';
  import { userStore } from '$lib/state/User.svelte';
  import { formatDate, scrollToInput } from '$lib/utils';

  let backUrl: string = '/#/profile';
  let inputValue: string = $state('');
  let email_origin: DataOrigin | undefined = $state();
  let email_last_update: Date | undefined = $state();

  onMount(() => {
    if (!userStore.connected) {
      goto('/');
      return;
    } else {
      const identity = userStore.connected.identity;
      const currentValue = identity.email;
      inputValue = currentValue || '';
      email_origin = identity.dataDetails.email.origin;
      email_last_update = identity.dataDetails.email.lastUpdate;
    }
  });

  const navigateToPreviousPage = async () => {
    goto(backUrl);
  };

  const cancel = async () => {
    await navigateToPreviousPage();
  };

  const submit = async () => {
    if (userStore.connected && inputValue) {
      userStore.connected.setEmail(inputValue);
      console.log('Updated the email to', inputValue);
      toastStore.addToast('Information bien enregistrée !', 'success', 3000, false);
    }
    await navigateToPreviousPage();
  };
</script>

<PageWrapper>
  {#snippet header({ scrolled })}
    <NavWithBackButton title="Contact" {backUrl} {scrolled} />
  {/snippet}

  {#snippet content()}
    <div class="content-container" data-testid="container">
      <p>Vous pouvez modifier uniquement les champs ci-dessous.</p>

      <form autocomplete="on">
        <fieldset class="fr-fieldset">
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
                onfocus={scrollToInput}
              >
            </div>
          </div>
        </fieldset>
      </form>

      {#if email_origin == 'user' && email_last_update}
        <div class="data-update-info">
          Vous avez modifié cette information le
          {formatDate(email_last_update)}.
        </div>
      {/if}
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
  .content-container {
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
