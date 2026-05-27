<script lang="ts">
  import { mount, onMount, unmount } from 'svelte';
  import LogoutFooter from './LogoutFooter.svelte';

  interface Props {
    footerTarget?: HTMLElement | null;
    getFooterTarget?: (() => HTMLElement | null) | null;
    onClose?: (() => void) | null;
  }

  let { footerTarget = null, getFooterTarget = null, onClose = null }: Props = $props();

  let footerInstance: Record<string, unknown> | null = null;

  onMount(() => {
    const target = getFooterTarget?.() ?? footerTarget;
    if (!target) {
      return;
    }

    if (footerInstance) {
      unmount(footerInstance);
      footerInstance = null;
    }
    footerInstance = mount(LogoutFooter, {
      target,
      props: { onClose },
    });

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
