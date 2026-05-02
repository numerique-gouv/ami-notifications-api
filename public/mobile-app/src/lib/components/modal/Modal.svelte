<script lang="ts">
  import { type Component, mount, onMount, tick, unmount } from 'svelte';

  type MountedInstance = ReturnType<typeof mount>;

  interface ModalProps {
    footerTarget: HTMLElement;
    onClose: () => void;
    [key: string]: unknown;
  }

  let {
    id,
    title,
    component,
    onCloseCustom = () => {},
    props = {},
  }: {
    id: string;
    title: string;
    component: Component<Record<string, unknown>>;
    onCloseCustom?: () => void;
    props?: Record<string, unknown>;
  } = $props();

  let modalElement: HTMLDialogElement;
  let mountTarget: HTMLDivElement;
  let footerTarget: HTMLDivElement;
  let instance: MountedInstance | null = null;

  const dsfrModal = () => {
    if (typeof window.dsfr === 'function') {
      return window.dsfr(modalElement).modal;
    }
    return null;
  };

  const destroyInstance = () => {
    if (!instance) {
      return;
    }
    onCloseCustom();
    const instanceToDestroy = instance;
    instance = null;
    setTimeout(() => unmount(instanceToDestroy), 300);
  };

  const onClose = () => {
    dsfrModal()?.conceal();
  };

  export const open = async () => {
    const modalProps: ModalProps = {
      ...props,
      footerTarget,
      onClose: onClose,
    };

    instance = mount(component, {
      target: mountTarget,
      props: modalProps,
    });

    dsfrModal()?.disclose();
  };

  onMount(() => {
    modalElement.addEventListener('dsfr.conceal', destroyInstance);
    return () => modalElement.removeEventListener('dsfr.conceal', destroyInstance);
  });
</script>

<dialog class="fr-modal" {id} aria-labelledby="{id}-title" bind:this={modalElement}>
  <div class="fr-container">
    <div class="fr-grid-row fr-grid-row--center">
      <div class="fr-col-12">
        <div class="fr-modal__body">
          <div class="fr-modal__content">
            <h2 class="fr-modal__title" id="{id}-title">{title}</h2>
            <div bind:this={mountTarget}></div>
          </div>
          <div class="fr-modal__footer" bind:this={footerTarget}></div>
        </div>
      </div>
    </div>
  </div>
</dialog>

<style>
  .fr-modal {
    &:after,
    &:before {
      flex: 1 0 10%;
      height: 10%;
      width: 0;
    }
    &:after {
      content: "";
    }
    .fr-modal__body {
      border-radius: 1.75rem;
    }
    .fr-modal__content {
      padding: 1.5rem 1.5rem 0 1.5rem;
      margin-bottom: 2.5rem;
    }
    .fr-modal__footer {
      padding: 1.5rem;
    }
  }
</style>
