<script lang="ts">
  import LightModal, {
    type LightModalProps,
  } from '$lib/components/modal/LightModal.svelte';

  type Props = Omit<LightModalProps, 'centered'>;
  let props: Props = $props();
</script>

<LightModal {...props} centered />
