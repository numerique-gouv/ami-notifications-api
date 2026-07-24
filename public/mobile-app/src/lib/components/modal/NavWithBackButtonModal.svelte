<script lang="ts">
  interface Props {
    onClick: () => void;
    title?: string;
  }
  let { onClick, title }: Props = $props();
</script>

<nav>
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
    <div class="title">
      <h2>{title}</h2>
    </div>
  {/if}
</nav>

<style>
  nav {
    background-color: white;
    padding: 0;
    margin-bottom: 0.5rem;
    .back-button-wrapper {
      position: absolute;
      .back-button {
        margin-bottom: 0.5rem;
        color: var(--text-active-blue-france);
      }
    }
    .title {
      padding-left: 2.5rem;
      padding-top: 0rem;
      h2 {
        line-height: 2.5rem;
        margin-bottom: 0;
        font-size: 18px;
      }
    }
  }
</style>
