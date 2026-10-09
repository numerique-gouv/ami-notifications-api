<script lang="ts">
  import { type Snippet } from 'svelte';

  export interface LightModalProps {
    modalContent: Snippet;
    centered?: boolean;
    onClose?: (() => void) | null;
    modalId?: string;
  }
  let {
    modalContent,
    centered = false,
    onClose = null,
    modalId,
  }: LightModalProps = $props();
  let dialog: HTMLDialogElement | null = null;
  let modalClass = $derived(centered ? 'dialog--centered' : '');
</script>
<dialog
  bind:this={dialog}
  id={modalId}
  aria-labelledby="{modalId}-title"
  class="modal fr-modal {modalClass}"
  data-testid="light-modal-{modalId}"
>
  <div class="fr-container fr-container--fluid fr-container-md">
    <div class="fr-grid-row fr-grid-row--center">
      <div class="fr-col-12 fr-col-md-8 fr-col-lg-6">
        <div class="fr-modal__body">
          <div class="drag-handle"></div>
          <div class="fr-modal__header">
            <button
              aria-controls="{modalId}"
              title="Fermer"
              type="button"
              id="button-6080"
              class="fr-btn--close fr-btn"
            >
              Fermer
            </button>
          </div>
          <div class="fr-modal__content">{@render modalContent?.()}</div>
        </div>
      </div>
    </div>
  </div>
</dialog>
<style>
  dialog {
    .drag-handle {
      width: 2rem;
      height: 0.25rem;
      border-radius: 100px;
      background-color: #79747e;
      margin: 0 auto 1.75rem;
    }
    .fr-modal__body {
      border-radius: 1.75rem 1.75rem 0 0;
    }
    &.dialog--centered {
      /* todo */
      .drag-handle {
        display: none;
      }
    }
  }
</style>
