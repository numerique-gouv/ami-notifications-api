<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { AutoPromoItem } from '$lib/auto-promo';

  interface Props {
    item: AutoPromoItem;
  }
  let { item }: Props = $props();
</script>

<div class="auto-promo-container">
  <div
    class="fr-tile fr-tile--sm fr-tile--no-border fr-enlarge-button fr-p-2w fr-background-contrast--blue-france"
  >
    <div class="fr-tile__body">
      <div class="fr-tile__content fr-pb-0">
        <h3 class="fr-tile__title fr-mb-0">
          <button type="button" onclick={()=>goto(item.link)}>{item.title}</button>
        </h3>
        <p class="fr-tile__desc fr-text--md">{item.description}</p>
      </div>
    </div>
    <div class="fr-tile__header fr-mb-1w">
      <div class="fr-tile__pictogram">
        <img class="auto-promo-icon" src="/remixicons/house.svg" alt="">
      </div>
    </div>
  </div>
</div>

<style>
  .auto-promo-container {
    .fr-tile {
      .fr-tile__title {
        &:before {
          background: none;
        }
        button {
          &:before {
            background: none;
          }
          &:after {
            top: 50%;
            right: 0.5rem;
            --icon-size: 1.25rem;
            -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
            mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
          }
        }
      }
      .fr-tile__pictogram {
        height: 3rem;
        width: 3rem;
      }
    }
  }
</style>
