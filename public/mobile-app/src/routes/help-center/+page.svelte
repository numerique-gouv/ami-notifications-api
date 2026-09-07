<script lang="ts">
  import { onMount } from 'svelte';
  import { PUBLIC_HELP_URL } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-navigation';
  import Icon from '$lib/components/Icon.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });

  const menuHelpCenter = [
    {
      isEnabled: true,
      url: PUBLIC_HELP_URL,
      label: 'J’ai besoin de l’aide de l’administration',
      iconClassName: 'fr-icon-customer-2-line',
      id: 'help',
    },
    {
      isEnabled: true,
      url: '/#/contact',
      label: 'Je rencontre un problème sur l’application',
      iconClassName: 'fr-icon-alert-line',
      id: 'contact',
    },
  ];
</script>

<div class="fr-container help-page">
  <NavWithBackButton title="Aide et contact" {backUrl} />

  <div class="help-page-content-container fr-pt-14w">
    <nav class="fr-sidemenu fr-m-0" aria-labelledby="fr-sidemenu-title">
      <div class="fr-sidemenu__inner">
        <div id="fr-sidemenu-wrapper">
          <ul class="fr-sidemenu__list">
            {#each menuHelpCenter as helpItem}
              {#if helpItem.isEnabled}
                <li class="fr-sidemenu__item fr-mb-4w fr-border-default--grey">
                  <button
                    type="button"
                    class="fr-sidemenu__link fr-p-3w fr-text--lg am-text--smbold"
                    data-testid={`button-${helpItem.id}`}
                    onclick={() => AMIGoto(helpItem.url)}
                  >
                    <Icon
                      className="{helpItem.iconClassName} fr-text-label--blue-france am-icon-24 fr-mr-2w"
                    />
                    <span class="label">{helpItem.label}</span>
                  </button>
                </li>
              {/if}
            {/each}
          </ul>
        </div>
      </div>
    </nav>
  </div>
</div>

<style>
  .help-page-content-container {
    .fr-sidemenu,
    .fr-sidemenu__item:before {
      box-shadow: none;
    }
    .fr-sidemenu__item {
      border-radius: 0.25rem;
    }
  }
</style>
