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

<NavWithBackButton title="" {backUrl} />

<div class="fr-container profile-content-container fr-pt-8w" data-testid="profile">
  <h1 class="fr-h2 fr-mb-2w">Mon profil</h1>

  <div class="fr-tile fr-p-3w fr-mb-2w am-profile-tile" id="tile-7519">
    <div class="fr-tile__body">
      <div class="fr-tile__content">
        <h2 class="fr-tile__title fr-h3">
          <span data-testid="fullname">{fullName}</span>
        </h2>
      </div>
    </div>
    <div class="fr-tile__header">
      <div class="fr-tile__pictogram">
        <div
          class="fr-text-title--blue-france fr-h4 fr-mb-0 am-profile--initial"
          data-testid="initial"
        >
          {initial}
        </div>
      </div>
    </div>
  </div>

  <SideMenu sideMenus={sideMenuEntries} />
</div>

<style>
  .am-profile-tile {
    .am-profile--initial {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      background-color: var(--blue-france-925-125-hover);
      border-radius: 50%;
    }
    .fr-tile__title::before {
      background-image: linear-gradient(
        0deg,
        var(--border-active-blue-france),
        var(--border-active-blue-france)
      );
    }
  }
</style>
