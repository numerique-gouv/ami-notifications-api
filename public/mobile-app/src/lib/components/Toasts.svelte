<script lang="ts">
  import { flip } from 'svelte/animate';
  import Toast from '$lib/components/Toast.svelte';
  import { toastStore } from '$lib/state/toast.svelte';
</script>

{#if toastStore.toasts.length}
  <div class="toasts">
    {#each toastStore.toasts as toast (toast.id)}
      <div animate:flip={{ duration: 200 }}>
        <Toast id="{toast.id}" title="{toast.title}" level="{toast.level}" />
      </div>
    {/each}
  </div>
{/if}

<style>
  .toasts {
    position: fixed;
    bottom: 1rem;
    z-index: 3;
    margin: 0 1rem;
    width: calc(100% - 2rem);
  }
</style>
