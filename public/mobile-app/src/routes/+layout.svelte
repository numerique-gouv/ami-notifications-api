<script>
import '@gouvfr/dsfr/dist/dsfr.min.css'
import '@gouvfr/dsfr/dist/utility/utility.min.css'
import { onMount } from 'svelte'

let { children } = $props()

onMount(async () => {
  await import('@gouvfr/dsfr/dist/dsfr.module.min.js')
})
</script>

{@render children()}
