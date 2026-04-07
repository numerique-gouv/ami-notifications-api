<script>
  import '@gouvfr/dsfr/dist/dsfr.min.css';
  import '@gouvfr/dsfr/dist/utility/utility.min.css';
  import '../app.css';
  import { onMount } from 'svelte';
  import { afterNavigate, beforeNavigate, goto } from '$app/navigation';
  import { env } from '$env/dynamic/public';
  import Toasts from '$lib/components/Toasts.svelte';
  import { initDsfr } from '$lib/dsfr';
  import { initMatomo, trackPageView } from '$lib/matomo';
  import { emit } from '$lib/nativeEvents';

  let { children } = $props();

  onMount(async () => {
    if (env.PUBLIC_WEBSITE_PUBLIC === undefined && window.NativeBridge === undefined) {
      // The web app isn't opened to the public yet, and it's not being served in a native application.
      goto('/#/forbidden');
    }
    await initDsfr();

    initMatomo();
  });

  beforeNavigate((navigation) => {
    const url = navigation.to?.url;
    if (!url) {
      return;
    }
    emit('navigateTo', url);
    const path = url.href.replace(url.origin, ''); // Remove the `https://xxxx.yyy:zzzz` part of the current url, keep eg `/#/settings`.
    if (window.NativeURLs?.includes(path)) {
      console.log(
        `Cancel navigation to ${url}, found an entry in the window.NativeURLs, let the mobile app handle it`
      );
      navigation.cancel();
    }
  });

  afterNavigate(() => {
    trackPageView(document.title);
  });
</script>

<Toasts />
{@render children()}
