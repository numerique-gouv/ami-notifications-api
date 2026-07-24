<script lang="ts">
  import { goto } from '$app/navigation';

  interface Props {
    backUrl: string;
  }
  let { backUrl }: Props = $props();

  const navigateToPreviousPage = async () => {
    goto(backUrl);
  };
</script>

<div class="back-button-wrapper">
  <button
    onclick={navigateToPreviousPage}
    data-testid="back-button"
    class="fr-btn fr-icon-arrow-left-line fr-btn--tertiary-no-outline"
  >
    Retour à la page précédente
  </button>
</div>

<style>
</style>
