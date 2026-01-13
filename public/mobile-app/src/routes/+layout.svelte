<script>
  import '@gouvfr/dsfr/dist/dsfr.min.css'
  import '@gouvfr/dsfr/dist/utility/utility.min.css'
  import { onMount } from 'svelte'
  import Toasts from '$lib/components/Toasts.svelte'

  let { children } = $props()

  onMount(async () => {
    // @ts-expect-error
    await import('@gouvfr/dsfr/dist/dsfr.module.min.js')
  })
</script>

<Toasts />
{@render children()}
