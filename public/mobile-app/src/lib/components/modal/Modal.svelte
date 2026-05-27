<script lang="ts">
  import { type Component, mount, onMount, tick, unmount } from 'svelte';
  import { slide } from 'svelte/transition';

  type MountedInstance = ReturnType<typeof mount>;

  interface ModalProps {
    footerTarget: HTMLElement | null;
    onClose: () => void;
    toggleModalElements: (visible: boolean) => void;
    [key: string]: unknown;
  }

  interface Props {
    id: string;
    title: string;
    component: Component<Record<string, unknown>>;
    closeButton?: boolean;
    centered?: boolean;
    onCloseCustom?: () => void;
    props?: Record<string, unknown>;
  }

  let {
    id,
    title,
    component,
    closeButton = true,
    centered = false,
    onCloseCustom = () => {},
    props = {},
  }: Props = $props();

  let modalElement: HTMLDialogElement;
  let mountTarget: HTMLDivElement;
  let footerTarget: HTMLDivElement | null = $state(null);
  let instance: MountedInstance | null = null;
  let modalElementsVisible: boolean = $state(true);

  const toggleModalElements = async (visible: boolean) => {
    modalElementsVisible = visible;
    await tick();
  };

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
      getFooterTarget: () => footerTarget,
      onClose,
      toggleModalElements,
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

<dialog
  class="fr-modal {centered ? 'fr-modal-centered' : ''}"
  {id}
  aria-labelledby="{id}-title"
  bind:this={modalElement}
>
  <div class="fr-container">
    <div class="fr-grid-row fr-grid-row--center">
      <div class="fr-col-12">
        <div class="fr-modal__body">
          <div class="fr-modal__content">
            {#if modalElementsVisible}
              {#if closeButton}
                <button
                  transition:slide
                  aria-controls="modal-action"
                  title="Fermer"
                  type="button"
                  class="fr-btn--close fr-btn"
                  onclick={onClose}
                >
                  <span class="fr-sr-only">Fermer</span>
                </button>
              {/if}
              <h2 class="fr-modal__title" id="{id}-title" transition:slide>{title}</h2>
            {/if}
            <div bind:this={mountTarget}></div>
          </div>
          {#if modalElementsVisible}
            <div
              class="fr-modal__footer"
              bind:this={footerTarget}
              transition:slide
            ></div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</dialog>

<style>
  .fr-modal {
    &:before {
      flex: 1 0 2%;
      height: 2%;
    }
    &:not(.fr-modal-centered):after {
      display: none;
    }
    .fr-container {
      padding: 0;
    }
    .fr-modal__body {
      border-radius: 0.5rem 0.5rem 0 0;
      .fr-modal__content {
        padding: 1.5rem 1rem 0 1rem;
        margin-bottom: 3.5rem;
        .fr-modal__title {
          margin-bottom: 1.5rem;
        }
      }
      .fr-modal__footer {
        padding: 2rem 1rem 1rem 1rem;
        background-image: none;
      }
    }
    .fr-btn--close {
      position: fixed;
      top: 1rem;
      right: 0;
      &::after {
        --icon-size: 1.5rem;
        margin-left: 0;
      }
    }
    &.fr-modal-centered {
      &:after,
      &:before {
        flex: 1 0 10%;
        height: 10%;
      }
      &:after {
        content: "";
      }
      .fr-container {
        padding-left: 1rem;
        padding-right: 1rem;
      }
      .fr-modal__body {
        border-radius: 1.75rem;
        .fr-modal__content {
          padding: 1.5rem 1.5rem 0 1.5rem;
          margin-bottom: 2.5rem;
          .fr-modal__title {
            margin-bottom: 1rem;
          }
        }
        .fr-modal__footer {
          padding: 1.5rem;
          background-image: none;
        }
      }
    }
    &:not(.fr-modal-centered) {
      .fr-container {
        min-height: 98%;
      }
      .fr-grid-row,
      .fr-col-12,
      .fr-modal__body {
        min-height: 100%;
      }
    }
  }
  @media (min-width: 48em) {
    .fr-modal.fr-modal-centered {
      .fr-modal__body {
        .fr-modal__content {
          margin-bottom: 4rem;
        }
      }
    }
  }
</style>
