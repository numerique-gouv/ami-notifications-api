<script lang="ts">
  import type { Snippet } from 'svelte';
  import { goto } from '$app/navigation';
  import BackButton from '$lib/components/BackButton.svelte';

  interface Props {
    backUrl: string;
    title?: string;
    children?: Snippet;
  }
  let { backUrl, children, title }: Props = $props();

  const navigateToPreviousPage = async () => {
    goto(backUrl);
  };
</script>

<nav>
  <BackButton {backUrl} />
  {#if title}
    <div class="title">
      <h2>{title}</h2>
      {#if children}
        {@render children()}
      {/if}
    </div>
  {:else}
    {#if children}
      {@render children()}
    {/if}
  {/if}
</nav>

<style>
  nav {
    padding: 1.5rem 1rem;
    .title {
      display: flex;
      h2 {
        flex-grow: 1;
        margin-bottom: 0;
      }
    }
  }
</style>
