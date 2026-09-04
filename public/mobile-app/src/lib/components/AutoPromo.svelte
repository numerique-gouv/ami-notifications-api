<script lang="ts">
  import Splide from '@splidejs/splide';
  import { onMount } from 'svelte';
  import { AutoPromoItem as Item } from '$lib/auto-promo';
  import AutoPromoItem from '$lib/components/AutoPromoItem.svelte';
  import '@splidejs/splide/dist/css/splide.min.css';
  import '@splidejs/splide/dist/css/splide-core.min.css';

  interface Props {
    items: Item[];
  }
  let { items }: Props = $props();

  let carousel = $state<HTMLDivElement | null>(null);
  let slideText: string = $state('');

  onMount(() => {
    if (carousel !== null) {
      const splide = new Splide(carousel, {
        type: 'loop',
        perPage: 1,
        arrows: true,
        drag: true,
        flickMaxPages: 1,
        snap: true,
        gap: '1rem',
        i18n: {
          prev: 'Diapositive précédente',
          next: 'Diapositive suivante',
          first: 'Aller à la première diapositive',
          last: 'Aller à la dernière diapositive',
          slideX: 'Aller à la diapositive %s',
          pageX: 'Aller à la page %s',
          play: 'Démarrer le défilement automatique',
          pause: 'Mettre en pause le défilement automatique',
          select: 'Sélectionner une diapositive à afficher',
        },
      });
      splide.mount();

      splide.on('moved', (newIndex) => {
        const slide = items[newIndex];
        slideText = `Slide : ${slide.title}`;
      });

      return () => splide.destroy();
    }
  });
</script>

{#if items.length > 1}
  <div
    class="auto-promo-container splide"
    role="group"
    aria-label="Carrousel de promotion"
    bind:this={carousel}
  >
    <div class="splide__track">
      <ul class="fr-raw-list splide__list">
        {#each items as item}
          <li aria-label={item.description} class="splide__slide">
            <AutoPromoItem item={item} className="" />
          </li>
        {/each}
      </ul>
      <div class="fr-sr-only" aria-live="polite" aria-atomic="true">{slideText}</div>
    </div>
  </div>
{:else if items.length == 1}
  {@const firstItem = items[0]}
  <div class="auto-promo-container">
    <AutoPromoItem item={firstItem} className="am-blue--arrow" />
  </div>
{/if}

<style lang="scss">
  .auto-promo-container {
    /* svelte-ignore css_unused_selector */
    :global {
      .splide__pagination {
        bottom: -1.5rem;
        .is-active {
          background-color: var(--text-active-blue-france);
        }
        .splide__pagination__page {
          opacity: 1;
          transform: scale(1);
          width: .375rem;
          height: .375rem;
        }
      }
      .splide__arrows {
        height: 0;
        overflow: hidden;
        opacity: 0;

        &:focus-within {
          opacity: 1;
          height: auto;
          overflow: visible;
        }
      }
      .splide__arrow {
        transform: translateY(-50%) scale(.5);
        top: 100%;
      }
    }
  }
</style>
