<script>
  import '@gouvfr/dsfr/dist/dsfr.min.css';
  import '@gouvfr/dsfr/dist/utility/utility.min.css';
  import { onMount } from 'svelte';
  import { afterNavigate } from '$app/navigation';
  import Toasts from '$lib/components/Toasts.svelte';
  import { initMatomo, trackPageView } from '$lib/matomo';

  let { children } = $props();

  onMount(async () => {
    // @ts-expect-error
    await import('@gouvfr/dsfr/dist/dsfr.module.min.js');

    initMatomo();
  });

  afterNavigate(() => {
    trackPageView(document.title);
  });
</script>

<Toasts />
{@render children()}
