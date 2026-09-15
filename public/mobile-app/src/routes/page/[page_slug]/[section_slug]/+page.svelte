<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import SideMenu from '$lib/components/SideMenu.svelte';
  import { buildContentPage, ContentPage, ContentSection } from '$lib/content-page';
  import { renderPageMarkdown } from '$lib/markdown';
  import type { SideMenuItem } from '$lib/side-menu';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let backUrl: string = '/';
  let { params } = $props();

  let page: ContentPage | null = $state(null);
  let section: ContentSection | null = $state(null);
  let tabSections: SideMenuItem[] = $state([]);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
    page = await buildContentPage(params.page_slug);
    section = page.getSectionBySlug(params.section_slug);
  });
</script>

<div class="fr-container content-page">
  {#if section}
    <NavWithBackButton title={section.title} {backUrl} />

    <div class="fr-pt-14w">{@html renderPageMarkdown(section.text)}</div>
  {/if}
</div>
