<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { AMIGoto } from '$lib/ami-goto';
  import {
    buildCheckList,
    CheckList,
    CheckListItem,
    CheckListSection,
  } from '$lib/checklist';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import SideMenu from '$lib/components/SideMenu.svelte';
  import { renderMarkdown } from '$lib/markdown';
  import type { SideMenuItem } from '$lib/side-menu';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let { params } = $props();

  let checklist_id = params.checklist_id;
  let section_id = params.section_id;
  let item_id = params.item_id;
  let backUrl = `/#/checklist/${checklist_id}/checks/${section_id}/`;
  let checklist: CheckList | null = $state(null);
  let section: CheckListSection | null = $state(null);
  let item: CheckListItem | null = $state(null);
  let tabLinks: SideMenuItem[] = $state([]);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
    }
    checklist = await buildCheckList(checklist_id);
    section = checklist.getSectionById(section_id);
    item = checklist.getItemById(item_id);
    item.links.forEach((link) => {
      tabLinks.push({
        url: link.url,
        title: link.text,
      });
    });
  });
</script>

<div class="fr-container step-page">
  {#if item}
    <NavWithBackButton title="" {backUrl}>
      <div class="settings-svg-icon"></div>
    </NavWithBackButton>

    <div class="fr-pt-14w item-content">
      <p>{@html renderMarkdown(item.text)}</p>
      <SideMenu sideMenus={tabLinks} />
    </div>
  {/if}
</div>
