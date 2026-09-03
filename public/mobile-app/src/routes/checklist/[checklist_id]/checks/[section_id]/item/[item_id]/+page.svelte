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

  let backUrl = $state('');
  let checklist: CheckList | null = $state(null);
  let section: CheckListSection | null = $state(null);
  let item: CheckListItem | null = $state(null);
  let tabLinks: SideMenuItem[] = $state([]);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
    }
    checklist = await buildCheckList(params.checklist_id);
    section = checklist.getSectionById(params.section_id);
    backUrl = section.url;
    item = checklist.getItemById(params.item_id);
    item.links.forEach((link) => {
      tabLinks.push({
        url: link.url,
        title: link.text,
      });
    });
  });
</script>

<div class="fr-container checklist-item-page">
  {#if item}
    <NavWithBackButton title="" {backUrl} />

    <div class="fr-pt-14w item-content">
      <p>{@html renderMarkdown(item.text)}</p>
      <SideMenu sideMenus={tabLinks} />
    </div>
  {/if}
</div>
