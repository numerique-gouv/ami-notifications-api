<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import PageWrapper from '$lib/components/PageWrapper.svelte';
  import type { Services, ServicesItem } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';

  let { params } = $props();

  let backUrl: string = '/#/services';
  let service: ServicesItem | null = $state(null);

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
        <div class="service-content">{service.description}</div>
      </div>
    {/if}
  {/snippet}

  {#snippet footer()}
    temp
  {/snippet}
</PageWrapper>
