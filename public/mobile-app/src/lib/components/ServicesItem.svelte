<script lang="ts">
  import type { ServicesItem } from '$lib/services';

  interface Props {
    item: ServicesItem;
    hasNonArchivedItems: boolean;
    goToService?: ((service: ServicesItem) => void) | null;
  }
  let { item, hasNonArchivedItems = false, goToService = null }: Props = $props();
</script>

<li class="fr-sidemenu__item">
  {#if !hasNonArchivedItems && goToService}
    <button
      type="button"
      class="fr-sidemenu__link"
      onclick={() => goToService(item)}
      data-testid="service-catalog-{item.id}"
    >
      <span class="services--item-details">
        <span class="services--item-label">{item.title}</span>
        <span class="services--item-description">{item.service_name}</span>
      </span>
      <span aria-hidden="true" class="icon fr-icon-arrow-right-s-line"></span>
    </button>
  {:else}
    <button
      data-fr-opened="false"
      aria-controls="services-item-{item.id}-modal"
      id="services-item-{item.id}-button"
      type="button"
      class="fr-sidemenu__link"
      data-testid="service-catalog-{item.id}"
    >
      <span class="services--item-details">
        <span class="services--item-label">{item.title}</span>
        <span class="services--item-description">{item.service_name}</span>
      </span>
      <span aria-hidden="true" class="icon fr-icon-arrow-right-s-line"></span>
    </button>
  {/if}
</li>

<style>
  .fr-sidemenu__item {
    button.fr-sidemenu__link {
      background: none;
      border: none;
      width: 100%;
      text-align: left;
      font: inherit;
      cursor: pointer;
      padding: 1.5rem 0;
      color: #000;
      --hover-tint: none;
      --active-tint: none;
      justify-content: space-between;
      span.services--item-details {
        display: flex;
        flex-direction: column;
        span.services--item-label {
          font-weight: 700;
          font-size: 16px;
        }
        span.services--item-description {
          font-weight: 400;
          font-size: 14px;
          line-height: 20px;
          color: var(--text-mention-grey);
        }
      }
      span.icon {
        color: var(--text-active-blue-france);
      }
    }
    &:last-child::before {
      box-shadow:
        0 -1px 0 0 var(--border-default-grey),
        inset 0 -1px 0 0 var(--border-default-grey);
    }
  }
</style>
