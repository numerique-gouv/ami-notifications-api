<script lang="ts">
  import { type Snippet } from 'svelte';

  export interface LightModalProps {
    modalContent: Snippet;
    centered?: boolean;
    modalId?: string;
  }
  let { modalContent, centered = false, modalId }: LightModalProps = $props();
  let dialog: HTMLDialogElement | null = null;
  let modalClass = $derived(centered ? 'am-modal--centered' : '');
</script>
<dialog
  bind:this={dialog}
  id={modalId}
  aria-labelledby="{modalId}-title"
  class="fr-modal am-modal modal {modalClass}"
  data-testid="light-modal-{modalId}"
>
  <div class="fr-container fr-container--fluid fr-container-md">
    <div class="fr-grid-row fr-grid-row--center">
      <div class="fr-col-12 fr-col-md-8 fr-col-lg-6">
        <div class="fr-modal__body">
          <div class=""></div>
          <div class="fr-modal__header">
            <button
              aria-controls="{modalId}"
              aria-label="Fermer"
              type="button"
              id="button-6080"
              class="fr-btn--close fr-btn"
            ></button>
          </div>
          <div class="fr-modal__content fr-mb-3v">{@render modalContent?.()}</div>
        </div>
      </div>
    </div>
  </div>
</dialog>
<style>
  .fr-modal.am-modal {
    .fr-modal__header {
      padding-top: 0.5rem;
      padding-bottom: 0;
    }
    .fr-btn--close {
      min-height: 2.5rem;
      padding-left: 0.5rem;
      padding-right: 0.5rem;
      &:after {
        margin: 0;
        --icon-size: 1.5rem;
      }
    }
    .fr-modal__body {
      border-radius: 1.75rem 1.75rem 0 0;
    }
    &.am-modal--centered {
      &:after {
        content: "";
        width: 0;
        height: 10%;
        flex: 1 0 10%;
      }
      .fr-modal__body {
        max-width: calc(100% - 3rem);
        margin: 0 auto;
        border-radius: 1.75rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
      }
    }
  }
</style>
