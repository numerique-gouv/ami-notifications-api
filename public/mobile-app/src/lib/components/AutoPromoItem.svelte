<script lang="ts">
  import Splide from '@splidejs/splide';
  import { onMount } from 'svelte';
  import { AutoPromoItem } from '$lib/auto-promo';
  import AmBlue from '$lib/components/AmBlue.svelte';
  import '@splidejs/splide/dist/css/splide.min.css';
  import '@splidejs/splide/dist/css/splide-core.min.css';

  interface Props {
    item: AutoPromoItem;
  }
  let { item }: Props = $props();

  /* carrousel */

  let carousel = $state<HTMLDivElement | null>(null);
  let slideText: string = $state('');

  const slidesTab = [
    {
      title: 'Vous déménagez bientôt ?',
      description: 'Retrouvez la liste des étapes clés',
      url: '/#1',
      image: 'camion.svg',
    },
    {
      title: 'Opération Tranquillité Vacances',
      description: 'Protégez votre domicile pendant votre absence',
      url: '/#2',
      image: 'house.svg',
    },
    {
      title: 'Renseignez votre adresse',
      description: 'Gagnez du temps en la renseignant une seule fois',
      url: '/#3',
      image: 'house.svg',
    },
  ];

  onMount(() => {
    const splide = new Splide(carousel, {
      type: 'loop',
      perPage: 1,
      arrows: true,
      drag: 'free',
      snap: true,
      gap: '1rem',
      /*live: false,*/
      /*padding: {right: '2rem'},*/
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
      const slide = slidesTab[newIndex];
      slideText = `Slide : ${slide.title}`;
    });

    return () => splide.destroy();
  });
</script>

{#if slidesTab.length > 1}
  <div
    class="auto-promo-container splide"
    role="group"
    aria-label="Carrousel de promotion"
    bind:this={carousel}
  >
    <div class="splide__track">
      <ul class="fr-raw-list splide__list">
        {#each slidesTab as slideItem}
          <li aria-label={slideItem.description} class="splide__slide">
            <AmBlue item={slideItem} />
          </li>
        {/each}
      </ul>
      <div class="fr-sr-only" aria-live="polite" aria-atomic="true">{slideText}</div>
    </div>
  </div>
{:else}
  <div class="auto-promo-container">
    <AmBlue
      item={{
      title: 'Vous déménagez bientôt ?',
      description: 'Retrouvez la liste des étapes clés',
      url: '/#1',
      image: 'camion.svg',
      class: 'am-blue--arrow',
    }}
    />
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
