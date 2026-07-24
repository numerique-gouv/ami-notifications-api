<script lang="ts">
  import { onMount, type Snippet } from 'svelte';

  interface Props {
    header: Snippet;
    footer: Snippet;
    centered?: boolean;
    onClose: () => void;
  }
  let { header, footer, centered = false, onClose }: Props = $props();
  let dialog: HTMLDialogElement | null = null;
  let modalClass = $derived(centered ? 'dialog--centered' : '');
  const handleClose = () => {
    onClose();
  };
  onMount(() => {
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
    dialog?.addEventListener('close', handleClose);
    return () => {
      dialog?.removeEventListener('close', handleClose);
    };
  });
  const closeDialog = () => {
    dialog?.close();
  };
  const handleBackdropClick = (event: MouseEvent) => {
    if (event.target === dialog) {
      closeDialog();
    }
  };
</script>
<dialog
  bind:this={dialog}
  class="modal {modalClass}"
  onclick={handleBackdropClick}
  data-testid="item-modal"
>
  <div>
    <button
      onclick={closeDialog}
      title="Fermer la modale"
      class="close-button fr-icon-close-line"
    ></button>
    <div class="drag-handle"></div>
    {@render header?.()}
    {@render footer?.()}
  </div>
</dialog>
<style>
  dialog {
    position: fixed;
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    margin: 0;
    width: 100%;
    max-width: 100%;
    transform: none;
    border-radius: 1.75rem 1.75rem 0 0;
    border: none;
    padding: 1rem 1rem 2rem;
    .close-button {
      position: absolute;
      top: 1rem;
      right: 1rem;
      padding: 0;
      color: var(--text-active-blue-france);
    }
    .drag-handle {
      width: 2rem;
      height: 0.25rem;
      border-radius: 100px;
      background-color: #79747e;
      margin: 0 auto 1.75rem;
    }
    &.dialog--centered {
      top: 50%;
      bottom: auto;
      left: 50%;
      right: auto;
      transform: translate(-50%, -50%);
      width: 90%;
      border-radius: 1.75rem;
      padding: 1.5rem;
      .close-button {
        display: none;
      }
      .drag-handle {
        display: none;
      }
    }
  }
  dialog::backdrop {
    background: var(--grey-50-1000);
    opacity: 64%;
  }
</style>
