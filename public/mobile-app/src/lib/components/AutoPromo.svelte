<script lang="ts">
  import Splide, { type Options } from '@splidejs/splide';
  import { onMount } from 'svelte';
  import { AutoPromo, buildAutoPromo, AutoPromoItem as Item } from '$lib/auto-promo';
  import AutoPromoItem from '$lib/components/AutoPromoItem.svelte';
  import '@splidejs/splide/dist/css/splide.min.css';
  import '@splidejs/splide/dist/css/splide-core.min.css';
  import { type Agenda, buildAgenda } from '$lib/agenda';
  import { buildFollowup, type Followup } from '$lib/followup';
  import {
    buildPersonalDataConsent,
    PersonalDataConsent,
  } from '$lib/personal-data-consent';

  interface Props {
    items: Item[];
  }
  let { items }: Props = $props();

  let followup: Followup | null = $state(null);
  let agenda: Agenda | null = $state(null);
  let autoPromo: AutoPromo | null = $state(null);
  let splide: Splide | null = null;
  let carousel = $state<HTMLDivElement | null>(null);
  const carouselOptions = {
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
  } as Options;
  let slideText: string = $state('');

  onMount(async () => {
    buildCarousel();
  });

  const buildCarousel = () => {
    if (carousel !== null && items) {
      splide = new Splide(carousel, carouselOptions);
      splide.mount();

      splide.on('moved', (newIndex) => {
        if (items) {
          const slide = items[newIndex];
          slideText = `Slide : ${slide.title}`;
        }
      });
    }
  };

  const onCloseModal = (hasAccepted: boolean) => {
    onCloseModalAsync(hasAccepted);
  };

  const onCloseModalAsync = async (hasAccepted: boolean) => {
    if (splide && hasAccepted === true) {
      followup = await buildFollowup();
      agenda = await buildAgenda(followup);
      const personalDataConsent: PersonalDataConsent = await buildPersonalDataConsent();
      autoPromo = buildAutoPromo(agenda, personalDataConsent);

      if (autoPromo?.items) {
        items = autoPromo.items;
        buildCarousel();
      }
    } else {
      const carouselContainer: HTMLElement | null =
        document.querySelector<HTMLElement>('#carousel-container');
      if (carouselContainer) {
        carouselContainer.remove();
      }
    }
  };
</script>

{#if items.length > 1}
  <div
    class="auto-mea-container splide"
    role="group"
    aria-label="Carrousel de promotion"
    bind:this={carousel}
  >
    <div class="splide__track">
      <ul class="fr-raw-list splide__list">
        {#each items as item}
          <li aria-label={item.description} class="splide__slide">
            <AutoPromoItem item={item} className="" onClose={onCloseModal} />
          </li>
        {/each}
      </ul>
      <div class="fr-sr-only" aria-live="polite" aria-atomic="true">{slideText}</div>
    </div>
  </div>
{:else if items.length == 1}
  {@const firstItem = items[0]}
  <div class="auto-mea-container">
    <AutoPromoItem item={firstItem} className="am-blue--arrow" onClose={onCloseModal} />
  </div>
{/if}

<style lang="scss">
  .auto-mea-container {
    /* svelte-ignore css_unused_selector */
    :global {
      .splide__pagination {
        bottom: -1.5rem;
        .splide__pagination__page {
          background-color: var(--grey-625-425);
          opacity: 1;
          transform: scale(1);
          width: .375rem;
          height: .375rem;
          transition: .2s width linear;
          &.is-active {
            background-color: var(--text-active-blue-france);
            width: .75rem;
            border-radius: 1.25rem;
          }
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
