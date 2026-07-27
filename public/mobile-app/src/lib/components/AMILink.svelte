<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { HTMLAnchorAttributes } from 'svelte/elements';
  import { AMIGoto, AMIUrl } from '$lib/ami-navigation';

  interface Props extends HTMLAnchorAttributes {
    url: string;
    silentLogin?: boolean;
    children: Snippet;
  }

  let { url, silentLogin = false, children, onclick, ...opts }: Props = $props();

  const newUrl: string = $derived(AMIUrl(url, silentLogin));

  function handleClick(
    e: MouseEvent & { currentTarget: EventTarget & HTMLAnchorElement }
  ) {
    if (typeof onclick === 'function') {
      onclick(e);
    }
    if (
      e.defaultPrevented ||
      e.metaKey ||
      e.ctrlKey ||
      e.shiftKey ||
      e.altKey ||
      e.button !== 0
    ) {
      return;
    }

    e.preventDefault();
    if (newUrl) {
      AMIGoto(newUrl);
    }
  }
</script>

<a href={newUrl} onclick={handleClick} {...opts}> {@render children()} </a>
