<script lang="ts">
  import { page } from '$app/state';
  import { AMIGoto } from '$lib/ami-navigation';

  const goToHomepage = () => {
    AMIGoto('/');
  };
</script>

<div class="technical-error">
  <div class="image-wrapper">
    <img class="error-icon" src="/remixicons/technical-error.svg" alt="">
  </div>
  <h1>Petit problème de notre côté...</h1>
  <div class="descriptive-text">
    <p class="am-text-mention-grey">
      Erreur {page.status}
      {#if page.error}
        - {page.error.message}
      {/if}
    </p>
    <p>Nous tentons de le résoudre rapidement.</p>
    <p>Vous pouvez éventuellement vérifier l’état de votre connexion et réessayer.</p>
  </div>
  <div class="action-buttons">
    <button
      class="fr-btn fr-icon-home-4-line fr-btn--icon-left"
      type="button"
      onclick="{goToHomepage}"
      data-testid="back-button"
    >
      Retour
    </button>
  </div>
</div>

<style>
  .technical-error {
    padding: 1.5rem 1rem;
    margin-top: 9rem;

    .image-wrapper {
      display: flex;
      justify-content: center;
      margin: 0 auto 1.5rem auto;
      max-width: 80%;
      height: 6rem;
    }
    h1 {
      margin-bottom: 0.5rem;
      font-size: 18px;
      line-height: 20px;
      font-weight: 700;
      text-align: center;
    }
    .descriptive-text {
      margin-bottom: 2.5rem;
      font-size: 16px;
      line-height: 24px;
      font-weight: 400;
      text-align: center;
    }
    .action-buttons {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      align-items: center;

      button {
        display: flex;
        justify-content: center;
      }
    }
  }
</style>
