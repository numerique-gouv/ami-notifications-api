<script lang="ts">
  import { onMount } from 'svelte';
  import { flip } from 'svelte/animate';
  import Toast from '$lib/components/Toast.svelte';
  import { toastStore } from '$lib/state/toast.svelte';

  let aboveMenu = false;

  onMount(async () => {
    if (document.getElementById('menu-footer')) {
      aboveMenu = true;
    }
  });
</script>

{#if toastStore.toasts.length}
  <div class="toasts {aboveMenu ? 'above-menu' : ''}">
    {#each toastStore.toasts as toast (toast.id)}
      <div animate:flip={{ duration: 200 }}>
        <Toast
          id="{toast.id}"
          title="{toast.title}"
          toastType="{toast.toastType}"
          duration="{toast.duration}"
          hasCloseLink="{toast.hasCloseLink}"
        />
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
  .above-menu {
    bottom: calc(68px + 1rem);
  }
</style>
