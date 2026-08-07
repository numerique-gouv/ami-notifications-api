<script lang="ts">
  import { onMount } from 'svelte';
  import { AutoPromoItem } from '$lib/auto-promo';

  interface Props {
    item: AutoPromoItem;
  }
  let { item }: Props = $props();
</script>

<div class="auto-promo-container">
  <div class="fr-tile fr-tile--sm fr-tile--no-border fr-enlarge-link fr-p-4v">
    <div class="fr-tile__body">
      <div class="fr-tile__content fr-pb-0">
        <h3 class="fr-tile__title"><a href="{item.link}">{item.title}</a></h3>
        <p class="fr-tile__desc">{item.description}</p>
      </div>
    </div>
    <div class="fr-tile__header">
      <div class="fr-tile__pictogram">
        <img class="auto-promo-icon" src="/remixicons/house.svg" alt="">
      </div>
    </div>
  </div>
</div>

<style>
  .auto-promo-container {
    .fr-tile {
      background-color: var(--blue-france-950-100);

      .fr-tile__body {
        .fr-tile__content {
          padding-bottom: 1rem;
          .fr-tile__title {
            font-size: 16px;
            line-height: 24px;
            font-weight: 700;
            &::before {
              background: none;
            }
            a {
              color: var(--text-active-blue-france);
              &::before {
                background: none;
              }
              &::after {
                color: var(--text-active-blue-france);
                top: 50%;
                right: 0.5rem;
                --icon-size: 1.25rem;
                -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
                mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
              }
            }
          }
          .fr-tile__desc {
            font-size: 16px;
            line-height: 24px;
            font-weight: 400;
          }
        }
      }
      .fr-tile__header {
        .fr-tile__pictogram {
          height: 3rem;
          width: 3rem;
        }
      }
    }
  }
</style>
