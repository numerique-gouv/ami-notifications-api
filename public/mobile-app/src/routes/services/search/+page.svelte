<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import ServicesSearchSkeleton from '$lib/components/skeletons/ServicesSearchSkeleton.svelte';
  import type { Followup } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import type { Services } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { skeletonDebugDelay } from '$lib/skeleton';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = $state('/#/services');

  let services: Services | null = $state(null);
  let followup: Followup | null = $state(null);

  const waitForPageData = async () => {
    await skeletonDebugDelay();
    [followup, services] = await Promise.all([buildFollowup(), buildServices()]);
  };

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
  });
</script>

<svelte:head>
  <title>Services - Rechercher un service</title>
</svelte:head>

<div class="services-search-page fr-px-2w">
  <NavWithBackButton
    className="not-sticky small-header"
    title="Rechercher un service"
    {backUrl}
  />

  <div class="services-search-container">
    {#await waitForPageData()}
      <ServicesSearchSkeleton />
    {:then pageDataLoaded}
      {#await import('$lib/components/Services.svelte') then { default: Services }}
        <Services followup={followup} services={services} />
      {/await}
    {/await}
  </div>
</div>
