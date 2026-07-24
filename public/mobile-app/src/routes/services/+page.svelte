<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-goto';
  import ServicesItemModal from '$lib/components/modal/ServicesItemModal.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import type { Followup } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import type { Services, ServicesItem } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';

  let services: Services | null = $state(null);
  let selectedServicesItem: ServicesItem | null = $state(null);
  let followup: Followup | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/');
      return;
    }

    followup = await buildFollowup();
    services = await buildServices();
    console.log($state.snapshot(services));
  });

  const getServiceUrl = async (service: ServicesItem) => {
    return await service.getServiceUrl();
  };

  const goToService = async (service: ServicesItem) => {
    const url = await service.getServiceUrl();
    AMIGoto(url, service.with_silent_login);
  };

  const clickOnService = (service: ServicesItem) => {
    const hasNonArchivedItems =
      followup?.hasNonArchivedItems(service.partner_id, service.item_type) || false;
    if (hasNonArchivedItems) {
      selectedServicesItem = service;
    } else {
      goToService(service);
    }
  };
</script>

<Navigation currentItem="services" />

<div class="services">
  <div class="services--title">
    <h2>Services</h2>
  </div>

  <div class="services--container" data-testid="services">
    <div class="preferences-content-container">
      <nav class="fr-sidemenu" aria-labelledby="fr-sidemenu-title">
        <div class="fr-sidemenu__inner">
          <div id="fr-sidemenu-wrapper">
            <ul class="fr-sidemenu__list">
              {#if services && services.items.length}
                {#each services.items as item}
                  <li class="fr-sidemenu__item">
                    <button
                      type="button"
                      class="fr-sidemenu__link"
                      onclick={() => clickOnService(item)}
                      data-testid="service-{item.id}"
                    >
                      <span class="services--item-details">
                        <span class="services--item-label">{item.title}</span>
                        <span class="services--item-description"
                          >{item.short_description}</span
                        >
                      </span>
                      <span
                        aria-hidden="true"
                        class="icon fr-icon-arrow-right-s-line"
                      ></span>
                    </button>
                  </li>
                {/each}
              {/if}
            </ul>
          </div>
        </div>
      </nav>
    </div>
  </div>
</div>

{#if selectedServicesItem}
  <ServicesItemModal bind:item={selectedServicesItem} />
{/if}

<style>
  .services {
    margin-bottom: 68px;
    .services--title {
      padding: 1.5rem 1rem;
    }
    .fr-sidemenu {
      padding: 0 1rem;
      box-shadow: none;
      margin: 0;
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
    }
  }
</style>
