<script lang="ts">
  import { AMIGoto } from '$lib/ami-navigation';
  import BlocSituation from '$lib/components/BlocSituation.svelte';
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

    <p class="fr-mb-1v fr-text--bold">Block perso non compléter :</p>

    <BlocSituation>
      {#snippet blocSituationContent()}
        <p class="fr-mb-3w am-text--smbold">
          Répondez à quelques questions pour personnaliser votre liste de choses à
          faire.
        </p>
        <button
          type="button"
          class="fr-btn fr-btn--lg fr-icon-arrow-right-s-line fr-btn--icon-right am-btn-w100"
          onclick={()=> AMIGoto('/#/step-form')}
        >
          Compléter ma situation
        </button>
      {/snippet}
    </BlocSituation>

    <p class="fr-mb-1v fr-text--bold">Block perso une fois complété :</p>
    <BlocSituation>
      {#snippet blocSituationContent()}
        <ul class="fr-raw-list fr-mb-2w">
          <li>Je vais avoir mon <strong>premier enfant</strong></li>
          <li>Je suis en <strong>couple</strong></li>
          <li>Mon conjoint dépend du <strong>régime général</strong></li>
          <li>
            Exemple d'une ligne plus longue qui passe <strong>sur deux lignes</strong>
          </li>
          <li>Je dépend du <strong>régime général</strong></li>
        </ul>
        <div class="am-perso--footer">
          <button
            type="button"
            class="fr-btn fr-btn--tertiary fr-icon-arrow-right-s-line fr-btn--icon-left"
            onclick={()=> AMIGoto('/#/step-form')}
          >
            Modifier
          </button>
          <button type="button" class="fr-btn fr-btn--tertiary">Recommencer</button>
        </div>
      {/snippet}
    </BlocSituation>
  </div>
</div>

<style lang="scss">
  .step-page {
    position: relative;
  }
  .am-perso--footer {
    display: flex;
    gap: 1rem;
  }
</style>
