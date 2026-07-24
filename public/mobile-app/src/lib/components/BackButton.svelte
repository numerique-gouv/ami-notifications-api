<script lang="ts">
  import { AMIGoto } from '$lib/ami-navigation';

  interface Props {
    backUrl: string;
  }
  let { backUrl }: Props = $props();

  const navigateToPreviousPage = async () => {
    AMIGoto(backUrl);
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
