<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import SideMenu from '$lib/components/SideMenu.svelte';
  import { buildContentPage, ContentPage } from '$lib/content-page';
  import type { SideMenuItem } from '$lib/side-menu';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let backUrl: string = '/';
  let { params } = $props();

  let page: ContentPage | null = $state(null);
  let tabSections: SideMenuItem[] = $state([]);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
    page = await buildContentPage(params.page_slug);
    page.sections.forEach((section) => {
      tabSections.push({
        url: section.url,
        title: section.title,
        id: `page-section-${section.slug}`,
      });
    });
  });
</script>

<div class="fr-container content-page">
  {#if page}
    <NavWithBackButton title={page.title} {backUrl} />

    <div class="fr-pt-14w">
      <SideMenu sideMenus={tabSections} />
    </div>
  {/if}
</div>
