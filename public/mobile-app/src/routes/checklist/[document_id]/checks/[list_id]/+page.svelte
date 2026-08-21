<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { renderMarkdown } from '$lib/markdown';
  import type { PageProps } from './$types';

  let { data, params }: PageProps = $props();

  let backUrl = `/#/checklist/${params.document_id}/`;

  const checkList = JSON.parse(window.localStorage[`checklists-${params.document_id}`])
    .lists[params.list_id];

  onMount(async () => {
    /*
       if (!userStore.connected) {
      goto('/#/login');
    }
     */
  });
</script>

<div class="fr-container contact-page">
  <NavWithBackButton title="{checkList.title}" {backUrl}>
    <div class="settings-svg-icon"></div>
  </NavWithBackButton>

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
        {#each checkList.items as checkItem, i}
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
                            name="checkboxes-small-{i}"
                            id="checkboxes-small-{i}-indeterminate"
                            type="checkbox"
                            aria-describedby="checkboxes-small-{i}-indeterminate-messages"
                          >
                          <label
                            class="fr-label fr-text--regular fr-m-0 fr-pt-2w fr-pb-5v fr-pr-3w fr-pl-7w "
                            for="checkboxes-small-{i}-indeterminate"
                          >
                            <span> {@html renderMarkdown(checkItem.text)} </span>
                          </label>
                        </div>
                        <!--
                      <button
                        type="button"
                        class="am-after-icon-arrow"
                        onclick={()=>goto("/")}
                        aria-label="Avant la fin du 3e mois de grossesse : passer le 1er examen prénatal, qui permet de faire la déclaration de grossesse"
                      ></button>
                      -->
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
</div>

<style lang="scss">
  .checklist-page-wrapper {
    ul,
    .fr-tile__title {
      width: 100%;
    }
    .fr-tile {
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
</style>
