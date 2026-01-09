<script lang="ts">
  import { goto } from '$app/navigation'

  const goToHomepage = () => {
    goto('/')
  }
</script>

<div class="technical-error">
  <div class="image-wrapper">
    <img
      class="error-icon"
      src="/remixicons/technical-error.svg"
      alt="Icône d'erreur technique"
    >
  </div>
  <h1>Petit problème de notre côté...</h1>
  <div class="descriptive-text">
    <p>Nous tentons de le résoudre rapidement. Réessayez plus tard.</p>
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
      margin-bottom: 1.5rem;
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
