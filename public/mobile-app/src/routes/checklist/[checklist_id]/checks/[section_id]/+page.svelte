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
  import { renderMarkdown } from '$lib/markdown';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let { params } = $props();

  let backUrl = $state('');
  let checklist: CheckList | null = $state(null);
  let section: CheckListSection | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
    }
    checklist = await buildCheckList(params.checklist_id);
    section = checklist.getSectionById(params.section_id);
    backUrl = checklist.url;
  });
</script>

<div class="fr-container checklist-section-page">
  {#if checklist && section}
    <NavWithBackButton title={section.title} {backUrl} />

    <div class="checklist-page-wrapper fr-pt-14w">
      <fieldset
        class="fr-fieldset fr"
        id="checkboxes-small"
        aria-labelledby="checkboxes-small-legend checkboxes-small-messages"
      >
        <legend
          class="fr-fieldset__legend--regular fr-fieldset__legend"
          id="checkboxes-small-legend"
        ></legend>
        <ul class="fr-raw-list fr-px-1w">
          {#each checklist.getItemsForSection(section.id) as item}
            <li>
              <div
                class="fr-tile fr-tile--sm fr-tile--horizontal fr-enlarge-button fr-p-0 fr-mb-2w"
                id="tile-7540"
              >
                <div class="fr-tile__body">
                  <div class="fr-tile__content fr-pb-0">
                    <div class="fr-tile__title fr-mb-0">
                      <div class="fr-fieldset__element fr-mb-0 fr-px-0">
                        <div class="fr-checkbox-group">
                          <div>
                            <input
                              name="checkboxes-small-{item.id}"
                              id="checkboxes-small-{item.id}-indeterminate"
                              data-testid="checkbox-{item.id}"
                              type="checkbox"
                              checked={item.checked}
                              onchange={(e) => item.markAs((e.target as HTMLInputElement).checked)}
                              aria-describedby="checkboxes-small-{item.id}-indeterminate-messages"
                            >
                            <label
                              class="fr-label fr-text--regular fr-m-0 fr-pt-2w fr-pb-5v fr-pr-3w fr-pl-7w "
                              for="checkboxes-small-{item.id}-indeterminate"
                            >
                              <span>{@html renderMarkdown(item.text)}</span>
                            </label>
                          </div>
                          {#if item.hasLinks()}
                            {#if item.links.length == 1}
                              <button
                                type="button"
                                class="am-after-icon-arrow"
                                onclick={()=>AMIGoto(item.links[0].url)}
                                aria-label="{item.links[0].text}"
                                data-testid="item-button-direct-link-{item.id}"
                              ></button>
                            {:else}
                              <button
                                type="button"
                                class="am-after-icon-arrow"
                                onclick={()=>AMIGoto(item.url)}
                                aria-label="Voir le détail de ce point"
                                data-testid="item-button-page-link-{item.id}"
                              ></button>
                            {/if}
                          {/if}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          {/each}
        </ul>
      </fieldset>
    </div>
  {/if}
</div>

<style lang="scss">
  .checklist-page-wrapper {
    ul,
    .fr-tile__title {
      width: 100%;
    }
    .fr-tile {
      .fr-tile__title::before {
        // force blue border as tiles are always clickable
        background-image: linear-gradient(0deg,var(--border-active-blue-france),var(--border-active-blue-france));
      }
      .fr-tile__title button {
        display: block;
        &:after {
          top: 50%;
          transform: translateY(-50%);
        }
      }
    }

    .fr-checkbox-group input[type="checkbox"] + label {
      &:before {
        margin: 0;
        left: 1.25rem;
        top: 50%;
        transform: translateY(-50%);
        width: 1.125rem;
        height: 1.125rem;
      }
      &:after {
        content: "";
        display: block;
        position: absolute;
        height: 100%;
        width: 3.5rem;
        left: 0;
        z-index: 20;
      }
    }

    .fr-checkbox-group input[type="checkbox"]:checked + label {
      background-color: var(--background-contrast-blue-france);
    }
  }
  .am-truncate-5lines {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 5;
    line-clamp: 5;
    overflow: hidden;
  }
</style>
