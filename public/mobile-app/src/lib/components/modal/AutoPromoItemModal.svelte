<script lang="ts">
  import { type Component, onMount } from 'svelte';

  interface Props {
    item_component_modal_name: string;
    modalId: string;
    onClose?: (hasAccepted: boolean) => void | null;
  }
  let { item_component_modal_name, modalId, onClose }: Props = $props();

  let ModalComponent: Component<Record<string, unknown>> | null = $state(null);

  onMount(async () => {
    const modalPath = `./${item_component_modal_name}.svelte`;
    ModalComponent = (await import(modalPath)).default;
  });

  const onCloseModal = (hasAccepted: boolean = false) => {
    if (onClose) {
      onClose(hasAccepted);
    }
  };
</script>

<svelte:component
  this={ModalComponent}
  modalId="{modalId}"
  onClose={onCloseModal}
  pageOrigin="homepage-autopromo"
></svelte:component>
