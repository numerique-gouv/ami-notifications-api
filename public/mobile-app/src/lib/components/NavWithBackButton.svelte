<script lang="ts">
  import type { Snippet } from 'svelte'
  import { goto } from '$app/navigation'
  import BackButton from '$lib/components/BackButton.svelte'

  interface Props {
    backUrl: string
    title?: string
    children?: Snippet
  }
  let { backUrl, children, title }: Props = $props()
  let scrolled = $state(false)

  const navigateToPreviousPage = async () => {
    goto(backUrl)
  }

  window.onscroll = () => {
    scrolled = document.body.scrollTop > 20 || document.documentElement.scrollTop > 20
  }
</script>

<nav class={[{scrolled}]}>
  <div class="backbutton-wrapper">
    <BackButton {backUrl} />
  </div>
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
    background-color: white;
    padding: 1.5rem 1rem;
    position: sticky;
    top: 0;
    transition: 0.4s;
    z-index: 1000;
    .backbutton-wrapper {
      position: absolute;
    }
    .title {
      padding-top: 2rem;
      transition: 0.4s;
      h2 {
        line-height: 2rem;
        margin-bottom: 0;
        transition: 0.4s;
      }
    }
    &.scrolled {
      padding-bottom: 0.5rem;
      .title {
        padding-left: 2rem;
        padding-top: 0rem;
        h2 {
          font-size: 18px;
          line-height: 1.5rem;
          transition: 0.4s;
        }
      }
    }
  }
</style>
