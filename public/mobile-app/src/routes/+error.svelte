<script lang="ts">
  import { onMount } from 'svelte'
  import { page } from '$app/state'

  onMount(() => {
    // https://svelte.dev/docs/kit/routing#error
    // If an error occurs during load, SvelteKit will render a default error page.
    // You can customise this error page on a per-route basis by adding an +error.svelte file.

    console.error('Page status: ', page.status)
    if (page.error) {
      console.error('Error message: ', page.error.message)
    }
  })
</script>

<div class="technical-error">
  <h1>Nous sommes désolés, une erreur s'est produite.</h1>
  <div class="descriptive-text">
    <p>Veuillez réessayer plus tard.</p>
    <p>(Veuillez éventuellement vérifier la connexion)</p>
  </div>
  <div class="action-buttons">
    <a
      data-sveltekit-reload
      href="/"
      class="fr-btn"
      type="button"
      data-testid="back-button"
    >
      Revenir à l'accueil
    </a>
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

      p:first-child {
        margin-bottom: 0.5rem;
      }
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
