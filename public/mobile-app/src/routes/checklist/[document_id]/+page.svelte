<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import type { PageProps } from './$types';

  let backUrl: string = '/';
  let { data, params }: PageProps = $props();

  const document_id = params.document_id;
  const doc = JSON.parse(window.localStorage[`checklists-${params.document_id}`]);

  onMount(async () => {
    /*
       if (!userStore.connected) {
      goto('/#/login');
    }
     */
  });
</script>

<div class="fr-container contact-page">
  <NavWithBackButton title="{doc.title}" {backUrl}>
    <div class="settings-svg-icon"></div>
  </NavWithBackButton>

  <div class="checklist-page-wrapper fr-pt-14w">
    <p>Les démarches à accomplir et les points à ne pas oublier</p>

    <ul>
      {#each doc.lists as checkList}
        <li>
          <button
            onclick={(e) => {return goto(`/#/checklist/${document_id}/checks/0`)}}
          >
            <span>{checkList.title}</span>
            <span>0/{checkList.items.length}</span>
          </button>
        </li>
      {/each}
    </ul>
  </div>
</div>
