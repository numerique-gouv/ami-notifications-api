<script lang="ts">
  import { goto } from '$app/navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import SideMenu from '$lib/components/SideMenu.svelte';

  let backUrl: string = '/#/services';

  const tabServices = [
    {
      isEnabled: true,
      url: '/#/checklist',
      title: 'Pendant la grossesse',
      iconClass: 'fr-icon-user-line',
      id: 'profile',
    },
    {
      isEnabled: true,
      url: '/#/checklist',
      title: 'Pendant la grossesse',
      desc: 'Faites-nous votre retour',
      id: 'profile',
    },
    {
      isEnabled: true,
      url: '/#/checklist',
      title: 'Pendant la grossesse',
      tag: '2/12',
      iconClass: 'fr-icon-user-line',
      id: 'profile',
    },
    {
      isEnabled: true,
      url: '/#/checklist',
      title: 'Pendant la grossesse',
      date: 'débuté le 08 juin à 12h15',
      tag: '5/18',
      iconClass: 'fr-icon-user-line',
      id: 'profile',
    },
    {
      isEnabled: true,
      url: '/#/checklist',
      title: 'Pendant la grossesse',
      date: 'débuté le 08 juin à 12h15',
      desc: 'Faites-nous votre retour',
      tag: '1/20',
      iconClass: 'fr-icon-user-line',
      id: 'profile',
    },
    {
      isEnabled: true,
      url: '/#/2',
      title: 'Après la naissance',
      iconClass: 'fr-icon-settings-3-line',
      id: 'preferences',
    },
    {
      isEnabled: true,
      url: '/#/3',
      title: 'test',
      iconClass: 'fr-icon-question-answer-line',
      id: 'tes',
    },
  ];
</script>

<div class="fr-container step-page">
  <NavWithBackButton title="" {backUrl}>
    <div class="settings-svg-icon"></div>
  </NavWithBackButton>
  <div class="fr-pt-8w">
    <h1 class="fr-h2 am-truncate-3lines">Je deviens parent</h1>
    <p class="">Les démarches à accomplir et les points à ne pas oublier</p>
    <SideMenu sideMenus={tabServices} />

    <div class="fr-p-2w fr-mb-2w fr-background-contrast--blue-france">
      <p
        class="fr-badge fr-badge--sm am-badge--user fr-icon-user-fill fr-badge--icon-left fr-mb-2w"
      >
        Ma situation
      </p>
      <p class="fr-mb-3w am-text--smbold">
        Répondez à quelques questions pour personnaliser votre liste de choses à faire.
      </p>
      <button
        type="button"
        class="fr-btn fr-btn--lg fr-icon-arrow-right-s-line fr-btn--icon-right am-btn-w100"
        onclick={()=> goto('/#/step-form')}
      >
        Compléter ma situation
      </button>
    </div>
  </div>
</div>

<style lang="scss">
  .step-page {
    position: relative;
  }
</style>
