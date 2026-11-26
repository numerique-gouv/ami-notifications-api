<script lang="ts">
  import { onMount } from 'svelte';
  import { Item } from '$lib/agenda';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import SideMenu from '$lib/components/SideMenu.svelte';
  import type { SideMenuItem } from '$lib/side-menu';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = $state('/#/agenda');

  let sideMenuEntries: SideMenuItem[] = $state([
    {
      isEnabled: true,
      url: '/#/agenda/filters/themes',
      title: 'Thèmes',
      id: 'themes',
    },
    {
      isEnabled: true,
      url: '/#/preferences/zones/',
      title: 'Zones scolaires',
      id: 'zones',
    },
  ]);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });
</script>

<svelte:head>
  <title>Filtres</title>
</svelte:head>

<NavWithBackButton title="" {backUrl} />

<div class="filters-container fr-pt-8w fr-px-2w">
  <h1 class="fr-h2 fr-mb-4w">Filtres</h1>
  <SideMenu sideMenus={sideMenuEntries} />
</div>
