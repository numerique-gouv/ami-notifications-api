<script lang="ts">
  import { goto } from '$app/navigation'

  const goToHomepage = () => {
    goto('/')
  }
</script>

<div class="network-error">
  <div class="image-wrapper">
    <img
      class="error-icon"
      src="/remixicons/connection-lost.svg"
      alt="Icône d'erreur de connexion"
    >
  </div>
  <h1>Problème de connexion Internet</h1>
  <div class="descriptive-text">
    <p>
      Vérifiez votre réseau (données mobiles ou Wi-Fi) et relancez l'application pour
      vous connecter.
    </p>
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
  .network-error {
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
