<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';

  let { status, error } = $props();
  let retrying = $state(false);
  let hasTriedAutoRetry = $state(false);

  function shouldAutoRetry() {
    return (
      navigator.onLine &&
      !retrying &&
      !hasTriedAutoRetry &&
      (status === 0 || error?.message?.includes('network') || !error)
    );
  }

  async function attemptRetry() {
    if (!navigator.onLine || retrying) return;

    retrying = true;
    hasTriedAutoRetry = true;

    try {
      await goto(window.location.pathname, {
        invalidateAll: true,
        replaceState: true,
      });
    } catch (e) {
      window.location.reload();
    } finally {
      retrying = false;
    }
  }

  onMount(() => {
    if (browser && shouldAutoRetry()) {
      setTimeout(attemptRetry, 1000);
    }

    if (browser) {
      const handleOnline = () => {
        if (shouldAutoRetry()) {
          setTimeout(attemptRetry, 500);
        }
      };

      window.addEventListener('online', handleOnline);
      return () => window.removeEventListener('online', handleOnline);
    }
  });

  const goToHomepage = () => {
    goto('/', { invalidateAll: true });
  };
</script>

<div class="technical-error">
  <h1>Nous sommes désolés, une erreur s'est produite.</h1>
  <div class="descriptive-text">
    <p>Veuillez réessayer plus tard.</p>
    <p>(Veuillez éventuellement vérifier la connexion)</p>
  </div>
  <div class="action-buttons">
    <button
      class="fr-btn"
      type="button"
      onclick="{goToHomepage}"
      data-testid="back-button"
    >
      Revenir à l'accueil
    </button>
  </div>
</div>

<style>
  .technical-error {
    padding: 1.5rem 1rem;
    margin-top: 9rem;

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
