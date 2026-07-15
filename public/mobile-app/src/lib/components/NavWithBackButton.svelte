<script lang="ts">
  import type { Snippet } from 'svelte';
  import BackButton from '$lib/components/BackButton.svelte';

  interface Props {
    backUrl: string;
    logo?: string;
    logoAlt?: string;
    title?: string;
    scrolled?: boolean;
    children?: Snippet;
  }
  let {
    backUrl,
    logo,
    logoAlt,
    children,
    title,
    scrolled: scrolledProp = undefined,
  }: Props = $props();
  let scrolledInternal = $state(false);
  let scrolled = $derived(scrolledProp !== undefined ? scrolledProp : scrolledInternal);

  window.onscroll = () => {
    scrolledInternal =
      document.body.scrollTop > 20 || document.documentElement.scrollTop > 20;
  };
</script>

<nav class={[{scrolled}]}>
  <div class="backbutton-wrapper">
    <BackButton {backUrl} />
  </div>
  {#if logo}
    <div class="logo">
      <img src={logo} alt={logoAlt ? logoAlt : ""}>
    </div>
  {/if}
  {#if title}
    <div class={{title, withLogo: logo != undefined}}>
      <h1 class="fr-h3 fr-mb-0">{title}</h1>
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
    background-color: white;
    padding: 1.5rem 1rem;
    position: sticky;
    top: 0;
    transition: 0.4s;
    z-index: 1000;
    .backbutton-wrapper {
      position: absolute;
    }
    .logo {
      display: flex;
      justify-content: center;
      margin-bottom: 0.5rem;
      max-height: 80px;
      transition: 0.4s;
    }
    .title {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      padding-top: 2rem;
      transition: 0.4s;
      h1 {
        transition: 0.4s;
      }
      &.withLogo {
        padding-top: 0;
        text-align: center;
      }
    }

    &.scrolled {
      padding-bottom: 0.5rem;
      .logo {
        max-height: 40px;
        margin-bottom: 0;
      }
      .title {
        padding-left: 2rem;
        padding-top: 0rem;
        &.withLogo {
          padding-left: 0;
        }
      }
    }
  }
</style>
