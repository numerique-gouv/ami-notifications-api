<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import SideMenu from '$lib/components/SideMenu.svelte';
  import type { SideMenuItem } from '$lib/side-menu';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';

  let sideMenuEntries: SideMenuItem[] = $state([
    {
      isEnabled: true,
      url: '/#/preferences/consents',
      title: 'Suivi des démarches',
      id: 'consents',
    },
    {
      isEnabled: true,
      url: '/#/preferences/notifications',
      title: 'Notifications',
      id: 'notifications',
    },
    {
      isEnabled: true,
      url: '/#/preferences/zones',
      title: 'Zones scolaires',
      id: 'zones',
    },
    {
      isEnabled: true,
      url: '/#/preferences/personal-data-consent',
      title: 'Consentement données personnelles',
      id: 'personal-data-consent',
    },
  ]);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });
</script>

<svelte:head>
  <title>Préférences</title>
</svelte:head>

<div class="fr-container preferences-content-container" data-testid="preferences">
  <div class="preferences-content-container fr-pt-14w">
    <NavWithBackButton title="Préférences" {backUrl} />
    <SideMenu sideMenus={sideMenuEntries} />
  </div>
</div>
