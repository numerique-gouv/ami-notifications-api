<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import Card from '$lib/components/Card.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import SideMenu from '$lib/components/SideMenu.svelte';
  import type { UserIdentity } from '$lib/state/User.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';
  let initial: string = $state('');
  let fullName: string = $state('');

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
    initial = userStore.connected.getInitial();
    fullName = userStore.connected.getFullName();
  });

  let sideMenuEntries = [
    {
      isEnabled: true,
      url: '/#/profile/identity/',
      title: 'Mon identité',
      iconClass: 'fr-icon-account-line',
      id: 'identity',
    },
    {
      isEnabled: true,
      url: '/#/profile/addresses/',
      title: 'Mes coordonnées',
      iconClass: 'fr-icon-map-pin-user-line',
      id: 'addresses',
    },
  ];
</script>

<NavWithBackButton title="Mon profil" {backUrl} />

<div class="fr-container profile-content-container fr-pt-14w" data-testid="profile">
  <div>
    <span data-testid="initial">{initial}</span>
    <span data-testid="fullname">{fullName}</span>
  </div>
  <SideMenu sideMenus={sideMenuEntries} />
</div>
