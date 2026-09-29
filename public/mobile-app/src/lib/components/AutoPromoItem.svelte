<script lang="ts">
  import { type Component, onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import { AutoPromoItem as Item } from '$lib/auto-promo';

  interface Props {
    item: Item;
    className: string;
    index: number;
    onClose?: (hasAccepted: boolean, index: number) => void | null;
  }
  let { item, className, index, onClose }: Props = $props();

  let displayModal = $state(false);
  let ModalComponent: Component<Record<string, unknown>>;

  onMount(async () => {
    if (item.component_modal_name) {
      const modalPath = `./modal/${item.component_modal_name}.svelte`;
      ModalComponent = (await import(modalPath)).default;
    }
  });

  const openModal = () => {
    displayModal = true;
  };

  const onCloseModal = (hasAccepted: boolean) => {
    if (onClose) {
      onClose(hasAccepted, index);
    }
  };
</script>

<div
  class="am-blue fr-enlarge-button fr-p-2w fr-background-contrast--blue-france {className}"
>
  <div>
    <div class="am-blue__img fr-mb-1w" data-fr-inject-svg="true">
      <img class="am-icon" aria-hidden="true" src="/remixicons/{item.image}" alt="">
    </div>
    <h3 class="fr-mb-0 fr-text--md fr-text-label--blue-france">
      {#if item.link}
        <button
          class="fr-text--bold fr-p-0 am-blue__btn"
          type="button"
          onclick={()=>AMIGoto(item.link)}
        >
          {item.title}
        </button>
      {/if}
      {#if item.component_modal_name}
        <button
          class="fr-text--bold fr-p-0 am-blue__btn"
          type="button"
          onclick={openModal}
        >
          {item.title}
        </button>
      {/if}
    </h3>
    <p class="fr-text--md fr-m-0">{item.description}</p>
  </div>
</div>

{#if displayModal}
  <svelte:component
    this={ModalComponent}
    bind:displayModal={displayModal}
    onClose={onCloseModal}
  ></svelte:component>
{/if}

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
