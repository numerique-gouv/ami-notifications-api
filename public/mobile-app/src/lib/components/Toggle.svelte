<script lang="ts">
  import { type ToggleTag } from '$lib/types/components/toggletag';

  interface Props {
    id: string;
    label: string;
    isChecked: boolean;
    onChangeAction: (id: string, checked: boolean) => void;
    tags?: ToggleTag[];
  }
  let { id, label, isChecked, onChangeAction, tags = [] }: Props = $props();
</script>

<div class="fr-toggle">
  <input
    type="checkbox"
    class="fr-toggle__input"
    id={id}
    aria-describedby="toggle-messages toggle-hint"
    checked={isChecked}
    onchange={(e) => onChangeAction((e.target as HTMLInputElement).id, (e.target as HTMLInputElement).checked)}
    data-testid="{id}"
  >
  <label class="fr-toggle__label" for={id}>{label}</label>
  <div class="tags-container">
    {#each tags as tag}
      {#if tag.removable}
        <button
          class="fr-tag fr-tag--dismiss"
          type="button"
          aria-label="Retirer {tag.label}"
        >
          {tag.label}
        </button>
      {:else}
        <p class="fr-tag">{tag.label}</p>
      {/if}
    {/each}
  </div>
</div>

<style>
  .fr-toggle {
    padding: 1rem;
    &:has(.fr-tag) {
      padding-bottom: 0;
    }
    .fr-toggle__label {
      display: flex;
      position: relative;
      &:before {
        display: flex;
        position: absolute;
        right: -2rem;
        margin: 0;
      }
      &:after {
        position: absolute;
        left: auto !important;
        right: -1rem !important;
      }
    }
    .tags-container {
      padding-top: 0.5rem;
      p.fr-tag {
        background-color: var(--background-action-low-blue-france);
        color: var(--text-action-high-blue-france);
      }
    }
  }
</style>
