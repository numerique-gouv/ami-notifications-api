<script lang="ts">
  import { onMount } from 'svelte';
  import { hideBanner, isBannerHidden } from '$lib/banner';

  interface Props {
    id: string;
    title: string;
    description: string;
    bannerType: 'success' | 'info' | 'warning' | 'error';
  }
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
    class="fr-notice banner-wrapper {bannerType} fr-p-2w fr-mb-3w"
    data-testid="banner-{id}"
  >
    <div class="fr-container fr-p-0">
      <div class="fr-notice__body">
        <p>
          <span class="fr-notice__title">
            {#if bannerType === 'success'}
              <span
                class="banner-icon success fr-icon-success-fill"
                aria-hidden="true"
              ></span>
            {:else if bannerType === 'info'}
              <span
                class="banner-icon info fr-icon-information-fill"
                aria-hidden="true"
              ></span>
            {:else if bannerType === 'warning'}
              <span
                class="banner-icon warning fr-icon-warning-fill"
                aria-hidden="true"
              ></span>
            {:else if bannerType === 'error'}
              <span
                class="banner-icon error fr-icon-close-circle-fill"
                aria-hidden="true"
              ></span>
            {/if}
            <span>{title}</span>
          </span>
          <span class="fr-notice__desc fr-mt-1v"> {description} </span>
        </p>
        <button
          onclick={() => closeBanner(id)}
          title="Masquer le message"
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
  .banner-wrapper {
    color: var(--grey-50-1000);
    &.success {
      background-color: var(--green-emeraude-975-75);
    }
    &.info {
      background-color: var(--info-950-100);
    }
    &.warning {
      background-color: var(--yellow-moutarde-950-100);
    }
    &.error {
      background-color: var(--error-950-100);
    }
    .fr-notice__body {
      .fr-notice__title {
        display: flex;
        font-size: 16px;
        span.banner-icon {
          margin-right: 0.5rem;
          &.success::before {
            background-color: var(--success-425-625);
          }
          &.info::before {
            background-color: var(--info-425-625);
          }
          &.warning::before {
            background-color: var(--warning-425-625);
          }
          &.error::before {
            background-color: var(--error-425-625);
          }
        }
      }
    }
    .fr-btn--close {
      color: var(--text-active-blue-france);
    }
  }
</style>
