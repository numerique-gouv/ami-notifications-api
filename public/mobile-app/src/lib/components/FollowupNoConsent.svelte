<script>
  import { goto } from '$app/navigation';
  import FollowupInformation from '$lib/components/FollowupInformation.svelte';

  const gotoConsents = () => {
    goto('/#/preferences/consents');
  };
</script>

<div class="followup-no-consent-container fr-pt-2v">
  <p class="fr-mb-4v">Suivez vos démarches administratives au même endroit&nbsp;!</p>
  <div class="consent-action-button">
    <button
      class="fr-btn fr-btn--lg"
      type="button"
      onclick={gotoConsents}
      data-testid="consent-button"
    >
      Je veux suivre mes démarches
    </button>
  </div>
  <FollowupInformation />
</div>

<style lang="scss">
  .followup-no-consent-container {
    .consent-action-button {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      button {
        display: flex;
        justify-content: center;
        width: 100%;
      }
    }
  }
</style>
