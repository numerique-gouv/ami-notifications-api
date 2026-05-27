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
        title="Retour à la page précédente"
        aria-label="Retour à la page précédente"
        data-testid="back-button"
      >
        <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
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
    position: sticky;
    top: 0;
    z-index: 1000;
    .back-button-wrapper {
      position: absolute;
      .back-button {
        margin-bottom: 0.5rem;
        color: var(--text-active-blue-france);
        button {
          padding: 0;
        }
      }
    }
    .title {
      padding-left: 2rem;
      padding-top: 0rem;
      h2 {
        line-height: 2rem;
        margin-bottom: 0;
        font-size: 18px;
      }
    }
  }
</style>
