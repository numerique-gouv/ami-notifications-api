<script lang="ts">
  interface Props {
    title?: string
  }
  let { title }: Props = $props()

  const navigateToPreviousPage = async () => {
    window.history.back()
  }
</script>

<nav>
  <div class="back-button-wrapper">
    <button onclick={navigateToPreviousPage}
            title="Retour à la page précédente"
            aria-label="Retour à la page précédente"
            data-testid="back-button"
    >
      <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
    </button>
  </div>
  {#if title}
    <div class="title">
      <h2>{title}</h2>
    </div>
  {/if}
</nav>

<style>
  nav {
    padding: 1.5rem 1rem;
    .back-button-wrapper {
      margin-bottom: .5rem;
      color: var(--text-active-blue-france);
      button {
        padding: 0;
      }
    }
    .title {
      display: flex;
      h2 {
        flex-grow: 1;
        margin-bottom: 0;
      }
    }
  }
</style>
