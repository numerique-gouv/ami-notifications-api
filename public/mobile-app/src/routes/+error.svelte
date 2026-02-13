<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { page } from '$app/state'

  onMount(() => {
    console.error('Page status: ', page.status)
    if (page.error) {
      console.error('Error message: ', page.error.message)
    }
  })

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
  <h1>Nous sommes désolées, une erreur s'est produite.</h1>
  <div class="descriptive-text">
    <p>Veuillez réessayer plus tard.</p>
  </div>
  <div class="action-buttons">
    <button
      class="fr-btn"
      type="button"
      onclick="{goToHomepage}"
      data-testid="back-button"
    >
      C'est noté !
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
