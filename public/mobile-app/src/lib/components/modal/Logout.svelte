<script lang="ts">
  import { mount, unmount } from 'svelte';
  import LogoutFooter from './LogoutFooter.svelte';

  let {
    footerTarget = null,
    onClose = null,
  }: {
    footerTarget?: HTMLElement | null;
    onClose?: (() => void) | null;
  } = $props();

  let footerInstance: Record<string, unknown> | null = null;

  $effect(() => {
    if (footerTarget) {
      footerInstance = mount(LogoutFooter, {
        target: footerTarget,
        props: { onClose },
      });
    }
    return () => {
      if (footerInstance) {
        unmount(footerInstance);
        footerInstance = null;
      }
    };
  });
</script>

<p>
  En vous déconnectant, toutes les données enregistrées localement sur cet appareil
  (informations saisies, modifications et paramètres de personnalisation) seront
  supprimées.
</p>
