<script>
import 'https://sentry.incubateur.net/js-sdk-loader/e2423514591373cecd78c2eb2a939f40.min.js'
import '@gouvfr/dsfr/dist/dsfr.min.css'
import '@gouvfr/dsfr/dist/utility/utility.min.css'
import { onMount } from 'svelte'

let { children } = $props()

onMount(async () => {
  // @ts-ignore
  await import('@gouvfr/dsfr/dist/dsfr.module.min.js')
})
</script>

{@render children()}
