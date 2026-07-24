<script lang="ts">
  import { AMIGoto } from '$lib/ami-goto';
  import ZonePreferences from '$lib/components/modal/ZonePreferences.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let modalElementsVisible: boolean = $state(true);

  const toggleModalElements = async (visible: boolean) => {
    modalElementsVisible = visible;
  };

  const goToNotificationsWelcomePage = () => {
    AMIGoto('/#/notifications-welcome-page');
    /* to be replaced by:
     * AMIGoto('/#/welcome/notifications')
     * when app mobile is ready to intercept this new url
     */
  };
</script>

<div class="zones-welcome-page">
  <div class="zones-welcome-page-content">
    {#if modalElementsVisible}
      <h2>Zones scolaires</h2>
    {/if}
    <ZonePreferences toggleModalElements={toggleModalElements} />
  </div>
  {#if modalElementsVisible}
    <div class="zones-welcome-page-footer">
      <button
        type="button"
        class="fr-btn fr-btn--tertiary-no-outline"
        onclick={goToNotificationsWelcomePage}
        data-testid="skip-button"
      >
        Passer
        <span class="fr-icon-arrow-right-line" aria-hidden="true"></span>
      </button>
    </div>
  {/if}
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
