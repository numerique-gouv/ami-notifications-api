<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import PageWrapper from '$lib/components/PageWrapper.svelte';
  import { renderMarkdown } from '$lib/markdown';
  import type { Services, ServicesItem } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';

  let { params } = $props();

  let backUrl: string = '/#/services';
  let service: ServicesItem | null = $state(null);
  let date: string = $state('');

  const isValidDate = (d: Date | number) =>
    d instanceof Date && !Number.isNaN(d.getTime());

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
      return;
    }

    const services: Services = await buildServices();
    service = services.find(params.partner_id, params.item_type);
    console.log($state.snapshot(service));
    if (!service) {
      goto('/#/services');
    }

    const hash = window.location.hash;
    const url = new URL(hash.substring(1), window.location.origin);
    const stringFromUrl = url.searchParams.get('date') || '';
    const dateFormat: Intl.DateTimeFormatOptions = { month: 'long', day: 'numeric' };
    const locale = 'fr-FR';
    date = new Date().toLocaleDateString(locale, dateFormat);

    if (stringFromUrl !== '') {
      const dateFromUrl: Date = new Date(stringFromUrl);
      if (isValidDate(dateFromUrl)) {
        date = dateFromUrl.toLocaleDateString(locale, dateFormat);
      }
    }
  });
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
    temp
  {/snippet}
</PageWrapper>
