<script lang="ts">
  interface Props {
    onClick: () => void;
    title?: string;
  }
  let { onClick, title }: Props = $props();
</script>

<nav class="fr-mb-3v">
  <div class="back-button-wrapper">
    <div class="back-button">
      <button
        onclick={onClick}
        data-testid="back-button"
        class="fr-btn fr-icon-arrow-left-line fr-btn--tertiary-no-outline"
      >
        Retour à la page précédente
      </button>
    </div>
  </div>
  {#if title}
    <div class="title fr-pl-5w fr-pt-1w">
      <h2 class="fr-h6 fr-mb-0">{title}</h2>
    </div>
  {/if}
</nav>

<style>
  nav {
    .back-button-wrapper {
      position: absolute;
    }
  }
</style>
