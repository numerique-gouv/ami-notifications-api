<script lang="ts">
  import { mount, onMount, unmount } from 'svelte';
  import { goto } from '$app/navigation';
  import Toggle from '$lib/components/Toggle.svelte';
  import { Preferences, type ZoneInfo } from '$lib/state/preferences';
  import { userStore } from '$lib/state/User.svelte';
  import ZonePreferencesFooter from './ZonePreferencesFooter.svelte';

  let backUrl: string = '/#/preferences';
  let zoneInfos: ZoneInfo[] = $state([]);

  interface Props {
    footerTarget?: HTMLElement | null;
    getFooterTarget?: (() => HTMLElement | null) | null;
    onClose?: (() => void) | null;
    toggleModalElements?: ((visible: boolean) => void) | null;
  }

  let {
    footerTarget = null,
    getFooterTarget = null,
    onClose = null,
    toggleModalElements = null,
  }: Props = $props();

  let footerInstance: Record<string, unknown> | null = null;

  const mountFooter = () => {
    const target = getFooterTarget?.() ?? footerTarget;
    if (!target) {
      return;
    }
    if (footerInstance) {
      unmount(footerInstance);
      footerInstance = null;
    }
    footerInstance = mount(ZonePreferencesFooter, {
      target,
      props: { onClose },
    });
  };

  onMount(() => {
    if (!userStore.connected) {
      goto('/');
    } else {
      zoneInfos = userStore.connected.getZoneInfosFromPreferences();
    }

    mountFooter();

    return () => {
      if (footerInstance) {
        unmount(footerInstance);
        footerInstance = null;
      }
    };
  });

  const saveSettings = async (id: string, checked: boolean) => {
    if (!userStore.connected) {
      return;
    }
    const preferences = userStore.connected.identity.preferences;
    if (checked) {
      preferences.addZone(id);
    } else {
      preferences.removeZone(id);
    }
    userStore.connected.setPreferences(preferences);
  };
</script>

<div class="preferences-content-container">
  {#each zoneInfos as zoneInfo}
    <Toggle
      id={zoneInfo.zone}
      label={zoneInfo.zone}
      isChecked={zoneInfo.selected}
      onChangeAction={saveSettings}
      tags={zoneInfo.tags}
    />
  {/each}
</div>
