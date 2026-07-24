<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-goto';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import PageWrapper from '$lib/components/PageWrapper.svelte';
  import type { Followup } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import { renderMarkdown } from '$lib/markdown';
  import type { Services, ServicesItem } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';

  let { params } = $props();

  let backUrl: string = '/#/services';
  let service: ServicesItem | null = $state(null);
  let followup: Followup | null = $state(null);
  let hasNonArchivedItems: boolean = $state(false);
  let date: string = $state('');

  const isValidDate = (d: Date | number) =>
    d instanceof Date && !Number.isNaN(d.getTime());

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/');
      return;
    }

    const services: Services = await buildServices();
    const _service = services.find(params.partner_id, params.item_type);
    console.log($state.snapshot(_service));
    if (!_service) {
      AMIGoto('/#/services');
      return;
    }

    followup = await buildFollowup();
    const _hasNonArchivedItems = followup.hasNonArchivedItems(
      _service.partner_id,
      _service.item_type
    );

    const hash = window.location.hash;
    const url = new URL(hash.substring(1), window.location.origin);
    const stringFromUrl = url.searchParams.get('date') || '';
    const dateFormat: Intl.DateTimeFormatOptions = { month: 'long', day: 'numeric' };
    const locale = 'fr-FR';
    let _date = new Date().toLocaleDateString(locale, dateFormat);

    if (stringFromUrl !== '') {
      const dateFromUrl: Date = new Date(stringFromUrl);
      if (isValidDate(dateFromUrl)) {
        _date = dateFromUrl.toLocaleDateString(locale, dateFormat);
      }
    }

    // assign variables after all await calls
    service = _service;
    hasNonArchivedItems = _hasNonArchivedItems;
    date = _date;
  });

  const goToService = async () => {
    if (service === null) {
      return;
    }
    const url = await service.getServiceUrl();
    AMIGoto(url, service.with_silent_login);
  };

  const goToFollowup = () => {
    AMIGoto('/#/followup');
  };
</script>

<PageWrapper>
  {#snippet header({ scrolled })}
    {#if service}
      <NavWithBackButton title={service.title} {backUrl} {scrolled} />
    {/if}
  {/snippet}

  {#snippet content()}
    {#if service}
      <div class="service">
        <div class="service-content">
          {@html renderMarkdown(service.formatDescription(date))}
        </div>
      </div>
    {/if}
  {/snippet}

  {#snippet footer()}
    {#if service}
      <div class="service-action-buttons">
        {#if hasNonArchivedItems}
          <button
            class="fr-btn fr-btn--lg"
            type="button"
            onclick={goToFollowup}
            data-testid="followup-button"
          >
            Accéder à ma démarche
          </button>
          <button
            class="fr-btn fr-btn--lg fr-btn--tertiary"
            type="button"
            onclick={goToService}
            data-testid="service-button"
          >
            Faire une nouvelle démarche
          </button>
        {:else}
          <button
            class="fr-btn fr-btn--lg"
            type="button"
            onclick={goToService}
            data-testid="service-button"
          >
            Bénéficier de ce service
          </button>
        {/if}
      </div>
    {/if}
  {/snippet}
</PageWrapper>

<style>
  .service-action-buttons {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    button {
      display: flex;
      justify-content: center;
      width: 100%;
    }
  }
</style>
