<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    backUrl: string;
  }
  let { backUrl }: Props = $props();

  const navigateToPreviousPage = () => {
    window.location.href = backUrl;
  };
</script>

<div class="back-button-wrapper">
  <button
    onclick={navigateToPreviousPage}
    title="Retour à la page précédente"
    aria-label="Retour à la page précédente"
    data-testid="back-button"
  >
    <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
  </button>
</div>

<style>
  .back-button-wrapper {
    margin-bottom: 0.5rem;
    color: var(--text-active-blue-france);
    button {
      padding: 0;
    }
  }
</style>
