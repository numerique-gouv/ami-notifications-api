<script lang="ts">
  interface Props {
    id: string;
    label: string;
    isChecked: boolean;
    onChangeAction: (id: string, checked: boolean) => void;
  }
  let { id, label, isChecked, onChangeAction }: Props = $props();
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
</div>

<style>
  .fr-toggle {
    padding: 1rem;
    label.fr-toggle__label {
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
        left: auto;
        right: -1rem;
      }
    }
  }
</style>
