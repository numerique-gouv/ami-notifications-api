<script lang="ts">
  import { userStore } from '$lib/state/User.svelte';

  let {
    onClose = null,
  }: {
    onClose?: (() => void) | null;
  } = $props();
</script>

<ul class="fr-btns-group action-buttons">
  <li>
    <button
      class="fr-btn fr-btn--secondary cancel-button"
      type="button"
      onclick={onClose}
      data-testid="logout-cancel-button"
    >
      Annuler
    </button>
  </li>
  <li>
    <button
      class="fr-btn submit-button"
      type="button"
      onclick={userStore.logout}
      data-testid="logout-submit-button"
    >
      Confirmer
    </button>
  </li>
</ul>

<style>
  .action-buttons {
    background-color: var(--background-default-grey);
    display: flex;
    gap: 1rem;
    margin: 0;
    li {
      flex: 1;
      button {
        display: block;
        width: 100%;
        margin: 0;
      }
    }
  }
</style>
