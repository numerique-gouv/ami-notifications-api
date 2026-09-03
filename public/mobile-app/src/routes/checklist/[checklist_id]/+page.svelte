<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { buildCheckList, CheckList } from '$lib/checklist';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import SideMenu from '$lib/components/SideMenu.svelte';
  import type { SideMenuItem } from '$lib/side-menu';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let backUrl: string = '/#/services';
  let { params } = $props();

  let checklist: CheckList | null = $state(null);
  let tabSections: SideMenuItem[] = $state([]);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
    }
    checklist = await buildCheckList(params.checklist_id);
    checklist.sections.forEach((section) => {
      const items = (<CheckList>checklist).getItemsForSection(section.id);
      const checkedItems = items.filter((x) => x.checked);
      tabSections.push({
        url: section.url,
        title: section.title,
        tag: `${checkedItems.length}/${items.length}`,
        iconClass: 'fr-icon-calendar-check-line',
        id: `checklist-section-${section.id}`,
      });
    });
  });
</script>

<div class="fr-container checklist-page">
  {#if checklist}
    <NavWithBackButton title={checklist.title} {backUrl} />

    <div class="fr-pt-14w">
      <p>{checklist.description}</p>
      <SideMenu sideMenus={tabSections} />
    </div>
  {/if}
</div>
