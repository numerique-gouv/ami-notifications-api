<script lang="ts">
  import { type Snippet } from 'svelte';

  let { blocSituationContent }: { blocSituationContent: Snippet } = $props();
</script>

<div class="fr-p-2w fr-mb-3w fr-background-contrast--blue-france am-perso">
  <p
    class="fr-badge fr-badge--sm am-badge--user fr-icon-user-fill fr-badge--icon-left fr-mb-2w"
  >
    Ma situation
  </p>
  {@render blocSituationContent?.()}
</div>
