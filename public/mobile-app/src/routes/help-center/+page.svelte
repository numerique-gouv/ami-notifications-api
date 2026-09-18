<script lang="ts">
  import { onMount } from 'svelte';
  import { PUBLIC_HELP_URL } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });
</script>

<div class="fr-container help-page">
  <NavWithBackButton title="Aide et contact" {backUrl} />

  <div class="preferences-content-container fr-pt-14w">
    <nav class="fr-sidemenu" aria-labelledby="fr-sidemenu-title">
      <div class="fr-sidemenu__inner">
        <div id="fr-sidemenu-wrapper">
          <ul class="fr-sidemenu__list">
            <li class="fr-sidemenu__item">
              <button
                type="button"
                class="fr-sidemenu__link"
                data-testid="button-help"
                onclick={() => AMIGoto(PUBLIC_HELP_URL)}
              >
                <span class="label">J’ai besoin de l’aide de l’administration</span>
                <span aria-hidden="true" class="icon fr-icon-arrow-right-s-line"></span>
              </button>
            </li>
            <li class="fr-sidemenu__item">
              <button
                type="button"
                class="fr-sidemenu__link"
                data-testid="button-contact"
                onclick={() => AMIGoto("/#/contact")}
              >
                <span class="label">Je rencontre un problème sur l’application</span>
                <span aria-hidden="true" class="icon fr-icon-arrow-right-s-line"></span>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</div>
