<script lang="ts">
  import { onMount } from 'svelte';
  import { hideBanner, isBannerHidden } from '$lib/banner';

  interface Props {
    id: string;
    title: string;
    description: string;
    bannerType: 'success' | 'info' | 'warning' | 'error';
  }

  const tabTypeIcon = {
    info: 'fr-icon-information-fill',
    success: 'fr-icon-success-fill',
    warning: 'fr-icon-warning-fill',
    error: 'fr-icon-close-circle-fill',
  };

  let { id, title, description, bannerType }: Props = $props();

  let isHidden: boolean = $state(true);

  onMount(() => {
    isHidden = isBannerHidden(id);
  });

  const closeBanner = (id: string) => {
    isHidden = true;
    hideBanner(id);
  };
</script>

{#if !isHidden}
  <div
    class="fr-notice am-notice fr-mb-3w am-notice--{bannerType}"
    data-testid="banner-{id}"
  >
    <div class="fr-container">
      <div class="fr-notice__body">
        <p>
          <span class="fr-notice__title fr-mb-1v fr-text--md">
            <span
              class="banner-icon fr-mr-1w {tabTypeIcon[bannerType]}"
              aria-hidden="true"
            ></span>
            <span>{title}</span>
          </span>
          <span class="fr-notice__desc"> {description} </span>
        </p>
        <button
          onclick={() => closeBanner(id)}
          type="button"
          class="fr-btn--close fr-btn"
          data-testid="close-button"
        >
          Masquer le message
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .am-notice {
    &.am-notice--success {
      background-color: var(--green-emeraude-975-75);
      .banner-icon:before {
        background-color: var(--success-425-625);
      }
    }
    &.am-notice--info {
      background-color: var(--info-950-100);
      .banner-icon:before {
        background-color: var(--info-425-625);
      }
    }
    &.am-notice--warning {
      background-color: var(--yellow-moutarde-950-100);
      .banner-icon:before {
        background-color: var(--warning-425-625);
      }
    }
    &.am-notice--error {
      background-color: var(--error-950-100);
      .banner-icon:before {
        background-color: var(--error-425-625);
      }
    }
    .fr-notice__title {
      display: flex;
    }
    .fr-btn--close {
      color: var(--text-active-blue-france);
    }
  }
</style>
