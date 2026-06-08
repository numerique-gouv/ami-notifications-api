<script lang="ts">
  // This component can be used to have a "content" prop with some (optionnally) scrollable content,
  // and a "footer" prop with some action buttons that will always be visible at the bottom of the screen.
  // It also takes an optional "header" prop in case you need it to always be visible.

  import type { Snippet } from 'svelte';
  import { onMount } from 'svelte';

  interface Props {
    content: Snippet;
    footer: Snippet;
    header?: Snippet<[{ scrolled: boolean }]>;
  }
  let { content, footer, header }: Props = $props();
  let scrolled: boolean = $state(false);
  let contentEl: HTMLDivElement;
  let wrapperEl: HTMLDivElement;

  onMount(() => {
    wrapperEl.style.height = `${window.innerHeight}px`;
    console.log('innerHeight:', window.innerHeight);
  });
</script>

<div class="wrapper" bind:this={wrapperEl}>
  {#if header}
    <div class="header">{@render header({ scrolled })}</div>
  {/if}
  <div
    class="content"
    bind:this={contentEl}
    onscroll={() => { scrolled = contentEl.scrollTop > 20; console.log("scrolled", scrolled);}}
  >
    {@render content()}
  </div>
  <div class="footer">{@render footer()}</div>
</div>

<style>
  .wrapper {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;

    .content {
      flex-grow: 1;
      overflow: auto;
      padding: 1rem;
    }

    .footer {
      padding: 1rem;
    }
  }
</style>
