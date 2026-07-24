<script lang="ts">
  // This component can be used to have a "content" prop with some (optionnally) scrollable content,
  // and a "footer" prop with some action buttons that will always be visible at the bottom of the screen.
  // It also takes an optional "header" prop in case you need it to always be visible.

  import type { Snippet } from 'svelte';
  import { onMount } from 'svelte';

  interface Props {
    content: Snippet;
    footer: Snippet;
    header?: Snippet;
    className?: string;
  }
  let { content, footer, header, className = '' }: Props = $props();
</script>

<div class="wrapper content-header-fixe fr-container { className }">
  {#if header}
    <div class="header">{@render header()}</div>
  {/if}
  <div class="content">{@render content()}</div>
  <div class="footer fr-p-2w">{@render footer()}</div>
</div>

<style>
  .content-header-fixe {
    padding-top: 7rem;
    padding-bottom: 9rem;

    &.header-fix-with-logo {
      padding-top: 12rem;
    }
    .footer {
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      background-color: var(--background-default-grey);
    }
  }
</style>
