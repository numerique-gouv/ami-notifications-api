<script lang="ts">
  import type { Snippet } from 'svelte';
  import BackButton from '$lib/components/BackButton.svelte';

  interface Props {
    backUrl: string;
    logo?: string;
    logoAlt?: string;
    title?: string;
    children?: Snippet;
  }
  let { backUrl, logo, logoAlt, children, title }: Props = $props();
  let scrolled = $state(false);

  window.onscroll = () => {
    scrolled = document.body.scrollTop > 20 || document.documentElement.scrollTop > 20;
  };
</script>

<nav class={["fr-p-2w", {scrolled}]}>
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
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    min-height: 4rem;
    background-color: var(--background-default-grey);
    transition: 0.4s;
    z-index: 1000;
    .backbutton-wrapper {
      position: absolute;
      left: 0.5rem;
      z-index: 50;
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
      transition: 0.4s;
      transform: translateY(2.5rem);
      h1 {
        transition: 0.4s;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
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
        transform: translateY(0);
        h1 {
          transform: translateX(2rem);
          transition: 0.4s;
        }
        &.withLogo {
          padding-left: 0;
        }
      }
    }
  }
</style>
