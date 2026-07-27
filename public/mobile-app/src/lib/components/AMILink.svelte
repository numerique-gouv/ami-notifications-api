<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { HTMLAnchorAttributes } from 'svelte/elements';
  import { AMIGoto, AMIUrl } from '$lib/ami-navigation';

  interface Props extends HTMLAnchorAttributes {
    url: string;
    silentLogin?: boolean;
    variant?:
      | 'default'
      | 'menu-item'
      | 'menu-item-highlight'
      | 'see-all'
      | 'edit-address'
      | 'notifications'
      | 'preferences-item'
      | 'notification-item'
      | 'followup-item'
      | 'agenda-item';
    children: Snippet;
  }

  let {
    url,
    silentLogin = false,
    variant = 'default',
    children,
    onclick,
    class: className,
    ...opts
  }: Props = $props();

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

<a
  href={newUrl}
  onclick={handleClick}
  class={`am-link am-link--${variant} ${className ?? ''}`}
  {...opts}
>
  {@render children()}
</a>

<style>
  .am-link--menu-item,
  .am-link--menu-item-highlight {
    position: relative;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    background: none;
    padding: 0.75rem 0 0.375rem;
    height: 4.25rem;
  }
  .am-link--menu-item-highlight:before {
    z-index: -1;
    content: "";
    position: absolute;
    top: 0.5rem;
    background: var(--background-contrast-blue-france);
    border-radius: 1rem;
    width: 3.5rem;
    height: 2rem;
  }
  .am-link--see-all {
    font-size: 14px;
    font-weight: 400;
    line-height: 24px;
    color: var(--blue-france-sun-113-625);
    margin-right: 4px;
    display: inline-flex;
    gap: 4px;
  }
  .am-link--notifications[href] {
    background: none;
  }
  .am-link--preferences-item {
    padding: 1.5rem 0;
    font-weight: 500;
    color: #000;
    --hover-tint: none;
    --active-tint: none;
    justify-content: space-between;
  }
  .am-link--notification-item,
  .am-link--notification-item:not([href]) {
    font-size: 14px;
    color: var(--text-black-white-grey);
    &::before {
      background: none;
    }
    &::after {
      width: 0;
    }
  }
  .am-link--agenda-item.am-link--agenda-item,
  .am-link--agenda-item.am-link--agenda-item:not([href]),
  .am-link--agenda-item.am-link--agenda-item[href=""] {
    &::before {
      background: none;
    }
    &::after {
      bottom: 0.5rem;
      right: 0.5rem;
      --icon-size: 1.25rem;
      -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
      mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
    }
  }
  .am-link--agenda-item:not([href]),
  .am-link--agenda-item[href=""] {
    cursor: default;
    &::after {
      display: none;
    }
  }
  .am-link--edit-address.am-link--edit-address.am-link--edit-address {
    color: var(--grey-0-1000);
    &::after {
      color: var(--text-active-blue-france);
      bottom: 1.25rem;
      right: 1.25rem;
      --icon-size: 1rem;
    }
  }
  .am-link--followup-item.am-link--followup-item.am-link--followup-item {
    color: var(--text-action-high-blue-france);
    &::after {
      bottom: 0.5rem;
      right: 0.5rem;
      --icon-size: 1.25rem;
      -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
      mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
    }
  }
</style>
