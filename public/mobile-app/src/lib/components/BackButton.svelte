<script lang="ts">
  import { AMIBack } from '$lib/ami-navigation';

  interface Props {
    backUrl: string;
    allowHistoryBack?: boolean;
  }
  let { backUrl, allowHistoryBack }: Props = $props();
</script>

<div class="back-button-wrapper">
  <button
    onclick={() => AMIBack(backUrl, allowHistoryBack)}
    data-testid="back-button"
    class="fr-btn fr-icon-arrow-left-line fr-btn--tertiary-no-outline"
  >
    Retour à la page précédente
  </button>
</div>

<style>
</style>
