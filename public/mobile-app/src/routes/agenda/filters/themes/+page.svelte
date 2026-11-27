<script lang="ts">
  import { onMount } from 'svelte';
  import { THEMES } from '$lib/agenda';
  import { AMIBack, AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = $state('/#/agenda/filters');
  let selectedThemes: string[] = $state([]);

  const refreshPreferences = () => {
    if (!userStore.connected) {
      return;
    }
    selectedThemes = userStore.connected.identity.preferences.themes;
  };

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
    refreshPreferences();
  });

  const isThemeSelected = (id: string): boolean => {
    if (!userStore.connected) {
      return false;
    }
    const preferences = userStore.connected.identity.preferences;
    return preferences.themes.includes(id);
  };

  const saveThemes = async (id: string, checked: boolean) => {
    if (!userStore.connected) {
      return;
    }
    const preferences = userStore.connected.identity.preferences;
    if (checked) {
      preferences.addTheme(id);
    } else {
      preferences.removeTheme(id);
    }
    userStore.connected.setPreferences(preferences);
    refreshPreferences();
  };

  const clearThemes = async () => {
    if (!userStore.connected) {
      return;
    }
    const preferences = userStore.connected.identity.preferences;
    preferences.clearThemes();
    userStore.connected.setPreferences(preferences);
    refreshPreferences();
  };
</script>

<svelte:head>
  <title>Thèmes</title>
</svelte:head>

<div class="themes fr-px-2w">
  <NavWithBackButton title="Thèmes" {backUrl} />
  <div class="themes-container fr-pt-14w fr-pb-14w">
    {#if selectedThemes.length}
      <div class="themes-clear fr-pt-2w">
        <button
          type="button"
          class="fr-btn fr-btn--tertiary"
          onclick={clearThemes}
          data-testid="clear-themes"
          aria-label="Réinitialiser les thèmes"
        >
          Effacer tout
        </button>
      </div>
    {/if}
    {#each THEMES as theme}
      <div class="fr-pt-2w">
        <div class="fr-checkbox-group">
          <input
            name="checkbox"
            id={theme.id}
            type="checkbox"
            checked={selectedThemes.includes(theme.id)}
            onchange={(e) => saveThemes(theme.id, (e.target as HTMLInputElement).checked)}
            data-testid={theme.id}
          >
          <label class="fr-label" for={theme.id}>
            <div aria-hidden="true">
              <p
                class="fr-badge fr-badge--sm fr-badge--icon-left {theme.icon} {theme.badgeClassName}"
              ></p>
            </div>
            {theme.label}
          </label>
        </div>
      </div>
    {/each}
    <div class="fr-p-2w themes-footer">
      <button
        class="fr-btn fr-btn--secondary cancel-button am-btn-w100"
        type="button"
        onclick={() => AMIBack(backUrl)}
        data-testid="close-button"
      >
        Fermer
      </button>
    </div>
  </div>
</div>

<style>
  .themes {
    .themes-footer {
      z-index: 400;
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      background-color: var(--background-lifted-grey);
      border-top: 1px solid var(--border-default-grey);
    }
  }
</style>
