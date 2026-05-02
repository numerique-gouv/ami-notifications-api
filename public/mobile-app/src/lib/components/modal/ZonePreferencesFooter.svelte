<script lang="ts">
  interface Props {
    onClose?: (() => void) | null;
  }

  let { onClose = null }: Props = $props();
</script>

<button
  class="fr-btn fr-btn--secondary cancel-button"
  type="button"
  onclick={onClose}
  data-testid="close-button"
>
  Fermer
</button>

<style>
  button {
    display: block;
    width: 100%;
    margin: 0;
  }
</style>
