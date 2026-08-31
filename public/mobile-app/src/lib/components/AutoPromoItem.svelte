<script lang="ts">
  import { goto } from '$app/navigation';
  import { AutoPromoItem as Item } from '$lib/auto-promo';

  interface Props {
    item: Item;
    className: string;
  }
  let { item, className }: Props = $props();
</script>

<div
  class="am-blue fr-enlarge-button fr-p-2w fr-background-contrast--blue-france {className}"
>
  <div>
    <div class="am-blue__img fr-mb-1w" data-fr-inject-svg="true">
      <img class="am-icon" aria-hidden="true" src="/remixicons/{item.image}" alt="">
    </div>
    <h3 class="fr-mb-0 fr-text--md fr-text-label--blue-france">
      <button
        class="fr-text--bold fr-p-0 am-blue__btn"
        type="button"
        onclick={()=>goto(item.link)}
      >
        {item.title}
      </button>
    </h3>
    <p class="fr-text--md fr-m-0">{item.description}</p>
  </div>
</div>

<style lang="scss">

  .am-blue {
    height: 100%;
    text-align: center;
    display: flex;
    align-items: center;

    > div {
      width: 100%;
    }
    &__img {
      height: 3rem;
      width: 3rem;
      margin: 0 auto;

      .am-icon {
        display: block;
        height: 100%;
        width: 100%;
      }
    }
    &.fr-enlarge-button .am-blue__btn:before {
      outline-offset: -2px; 
    }
    &.am-blue--arrow {
      .am-blue__btn {
        &:after {
          position: absolute;
          content: "";
          display: block;
          height: 1.25rem;
          width: 1.25rem;
          -webkit-mask-size: 100% 100%;
          mask-size: 100% 100%;
          -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
          mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
          top: 50%;
          right: 0;
          transform: translateY(-50%);
          background-color: var(--text-active-blue-france);
        }
      }
    }
  }
</style>
