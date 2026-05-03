<script>
  import { goto } from '$app/navigation';
  import ZonePreferences from '$lib/components/modal/ZonePreferences.svelte';
  import { userStore } from '$lib/state/User.svelte';

  const goToHomepage = () => {
    goto('/');
  };
</script>

<div class="zones-welcome-page">
  <div class="zones-welcome-page-content">
    <h2>Zones scolaires</h2>
    <ZonePreferences />
  </div>
  <div class="zones-welcome-page-footer">
    <button
      type="button"
      class="fr-btn fr-btn--tertiary-no-outline"
      onclick={goToHomepage}
      data-testid="skip-button"
    >
      Passer
      <span class="fr-icon-arrow-right-line" aria-hidden="true"></span>
    </button>
  </div>
</div>

<style>
  .zones-welcome-page {
    padding: 1.5rem 1rem 0 1rem;
    h2 {
      font-size: 1.5rem;
      line-height: 2rem;
    }
  }
  .zones-welcome-page-footer {
    position: sticky;
    bottom: 0;
    background-color: var(--background-lifted-grey);
    padding: 1rem;
    button {
      text-decoration: underline;
      display: block;
      width: 100%;
      margin: 0;
      span::before {
        --icon-size: 1rem;
      }
    }
  }
</style>
