<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';

  let { status, error } = $props();
  let retrying = $state(false);
  let isOnline = $state(false);
  let cacheAvailable = $state(false);

  // Détecte état réseau + cache
  function checkNetworkStatus() {
    isOnline = navigator.onLine;

    // Vérifie si SW + cache actifs
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      caches.match(window.location.pathname).then((response) => {
        cacheAvailable = !!response;
      });
    }
  }

  async function smartRetry() {
    if (retrying || !isOnline) return;

    retrying = true;

    try {
      // 1. Essai navigation douce (SW devrait gérer le cache)
      await goto(window.location.pathname, {
        invalidateAll: true,
        replaceState: true,
      });
    } catch {
      // 2. Force refresh complet (SW servira cache si offline)
      window.location.reload();
    } finally {
      retrying = false;
    }
  }

  onMount(() => {
    if (browser) {
      checkNetworkStatus();

      const handleOffline = () => {
        isOnline = false;
      };

      // Écouteurs réseau
      window.addEventListener('online', checkNetworkStatus);
      window.addEventListener('offline', handleOffline);

      // Retry auto si réseau revenu ET cache disponible
      const handleOnline = () => {
        checkNetworkStatus();
        if (isOnline && cacheAvailable && status !== 404) {
          setTimeout(smartRetry, 800);
        }
      };

      window.addEventListener('online', handleOnline);

      return () => {
        window.removeEventListener('online', checkNetworkStatus);
        window.removeEventListener('offline', handleOffline);
        window.removeEventListener('online', handleOnline);
      };
    }
  });
</script>

<main class="error-container">
  <div class="error-header">
    <h1>Erreur {status || '?'}</h1>
    <p class="message">{error?.message || 'Impossible de charger la page'}</p>
  </div>

  <!-- Diagnostic réseau/cache -->
  <div class="status-grid">
    <div class="status-item">
      <span class="label">Réseau</span>
      <span class="status {isOnline ? 'online' : 'offline'}">
        {isOnline ? '🟢 En ligne' : '🔴 Hors ligne'}
      </span>
    </div>
    <div class="status-item">
      <span class="label">Cache</span>
      <span class="status {cacheAvailable ? 'online' : 'offline'}">
        {cacheAvailable ? '🟢 Disponible' : '⚪ Jamais chargé'}
      </span>
    </div>
  </div>

  <!-- Actions intelligentes selon contexte -->
  <div class="actions">
    <button
      class="retry-btn primary"
      disabled={retrying || (!isOnline && !cacheAvailable)}
      onclick={smartRetry}
    >
      {#if retrying}
        ⓷ Reconnexion...
      {:else if !isOnline && cacheAvailable}
        💾 Utiliser cache
      {:else if status === 404}
        🔍 Page inexistante
      {:else}
        🔄 Réessayer
      {/if}
    </button>

    {#if status === 404}
      <button class="home-btn" onclick={() => goto('/')}>🏠 Accueil</button>
    {/if}
  </div>

  <!-- Messages contextuels -->
  {#if !isOnline}
    <div class="hint">
      💡 Le service worker a mis vos pages en cache. Cliquez sur "Utiliser cache" pour
      continuer hors ligne.
    </div>
  {:else if !cacheAvailable}
    <div class="hint warning">
      ⚠️ Cette page n'a jamais été chargée (pas en cache). Rechargez une fois en ligne
      pour la rendre disponible offline.
    </div>
  {:else if status === 404}
    <div class="hint">❌ Cette page n'existe pas, même dans le cache.</div>
  {/if}
</main>

<style>
  .error-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 2rem;
    text-align: center;
    max-width: 600px;
    margin: 0 auto;
  }

  .status-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin: 2rem 0;
    width: 100%;
    max-width: 400px;
  }

  .status-item {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    background: #f8f9fa;
  }

  .status.online {
    background: #d4edda;
    color: #155724;
  }
  .status.offline {
    background: #f8d7da;
    color: #721c24;
  }

  .actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
    margin: 2rem 0;
  }

  .retry-btn,
  .home-btn {
    padding: 1rem 2rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    min-width: 160px;
  }

  .primary {
    background: #007acc;
    color: white;
    font-weight: 600;
  }
  .primary:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .home-btn {
    background: #6c757d;
    color: white;
  }

  .hint {
    margin-top: 2rem;
    padding: 1rem;
    background: #e7f3ff;
    border-radius: 8px;
    border-left: 4px solid #007acc;
  }

  .hint.warning {
    background: #fff3cd;
    border-left-color: #ffc107;
  }
</style>
