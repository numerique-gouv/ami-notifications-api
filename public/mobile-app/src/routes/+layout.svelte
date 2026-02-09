<script>
  import '@gouvfr/dsfr/dist/dsfr.min.css'
  import '@gouvfr/dsfr/dist/utility/utility.min.css'
  import { onMount } from 'svelte'
  import { afterNavigate, goto } from '$app/navigation'
  import { env } from '$env/dynamic/public'
  import Toasts from '$lib/components/Toasts.svelte'
  import { initDsfr } from '$lib/dsfr'
  import { initMatomo, trackPageView } from '$lib/matomo'

  let { children } = $props()

  onMount(async () => {
    if (env.PUBLIC_WEBSITE_PUBLIC === undefined && window.NativeBridge === undefined) {
      // The web app isn't opened to the public yet, and it's not being served in a native application.
      goto('/#/forbidden')
    }
    await initDsfr()

    initMatomo()
    trackPageView(document.title)
  })

  afterNavigate(() => {
    trackPageView(document.title)
  })
</script>

<Toasts />
{@render children()}
