<script lang="ts">
  import PersonalDataConsentModal from '$lib/components/modal/PersonalDataConsentModal.svelte';

  interface Props {
    item_component_modal_name: string;
    modalId: string;
    onClose?: (hasAccepted: boolean) => void | null;
  }
  let { item_component_modal_name, modalId, onClose }: Props = $props();

  const onCloseModal = (hasAccepted: boolean = false) => {
    if (onClose) {
      onClose(hasAccepted);
    }
  };
</script>

{#if item_component_modal_name === "PersonalDataConsentModal"}
  <PersonalDataConsentModal
    modalId="{modalId}"
    onClose={onCloseModal}
    pageOrigin="homepage-autopromo"
  />
{/if}
