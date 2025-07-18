<script lang="ts">
import { Capacitor } from '@capacitor/core'

const platform = Capacitor.getPlatform()
const isNativePlatform = Capacitor.isNativePlatform()
</script>

{#if (platform === 'ios')}
  This is an iOS application!
{:else if (platform === 'android')}
  This is an Android application!
{:else}
  This is a Web {#if isNativePlatform}application (PWA)!{:else}page{/if}
{/if}
