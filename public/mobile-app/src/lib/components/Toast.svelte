<script lang="ts">
  import { removeToast } from '$lib/components/toast'

  interface Props {
    id: string
    title: string
    level: string
  }
  let { id, title, level }: Props = $props()
</script>

<div class="fr-notice toast-wrapper {level}">
  <div class="fr-container">
    <div class="fr-notice__body">
      {#if level === 'success'}
        <span class="fr-icon-success-line" aria-hidden="true"></span>
      {/if}
      <p>{title}</p>
      <button
        onclick="{() => removeToast(id)}"
        title="Masquer le message"
        type="button"
        data-testid="close-button"
        class:fr-btn={level === 'success'}
        class:fr-btn--close={level === 'success'}
      >
        Fermer
      </button>
    </div>
  </div>
</div>

<style>
  .toast-wrapper {
    border-radius: 0.25rem;
    color: white;
    padding: 0.5rem 0;
    margin-top: 1rem;
    &.neutral {
      background-color: #343434;
    }
    &.success {
      background-color: #1b8644;
    }
    p {
      font-size: 14px;
    }
    button {
      font-size: 14px;
      text-decoration: underline;
    }
  }
</style>
