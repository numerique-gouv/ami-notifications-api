<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';

  let { data, status, error } = $props();

  let retrying = $state(false);
  let isOnline = $state(navigator.onLine);

  function attemptRetry() {
    if (!isOnline || retrying) return;

    retrying = true;

    goto(window.location.pathname, {
      invalidateAll: true,
      noScroll: true,
    })
      .catch(() => {
        window.location.reload();
      })
      .finally(() => {
        retrying = false;
      });
  }

  onMount(() => {
    if (browser) {
      const handleOnline = () => {
        isOnline = true;
        attemptRetry();
      };

      const handleOffline = () => {
        isOnline = false;
      };

      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);

      handleOnline();

      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
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
