<script>
  import '@gouvfr/dsfr/dist/dsfr.min.css';
  import '@gouvfr/dsfr/dist/utility/utility.min.css';
  import '../app.css';
  import { onMount } from 'svelte';
  import { afterNavigate } from '$app/navigation';
  import { env } from '$env/dynamic/public';
  import { AMIGoto } from '$lib/ami-goto';
  import Toasts from '$lib/components/Toasts.svelte';
  import { initDsfr } from '$lib/dsfr';
  import { initMatomo, trackPageView } from '$lib/matomo';

  let { children } = $props();

  onMount(async () => {
    if (env.PUBLIC_WEBSITE_PUBLIC === undefined && window.NativeBridge === undefined) {
      // The web app isn't opened to the public yet, and it's not being served in a native application.
      AMIGoto('/#/forbidden');
    }
    await initDsfr();

    initMatomo();
  });

  afterNavigate(() => {
    trackPageView(document.title);
  });
</script>

<Toasts />
{@render children()}
