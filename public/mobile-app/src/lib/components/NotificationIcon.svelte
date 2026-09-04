<script lang="ts">
  import { getDSFRIcon } from '$lib/dsfr-icon';

  interface Props {
    defaultIcon: string;
    icon?: string;
  }
  let { defaultIcon, icon = '' }: Props = $props();

  let checkedIcon = $derived(getDSFRIcon(icon, defaultIcon));
</script>

<span
  class="notification__icon fr-text-label--blue-france am-icon-20 {checkedIcon}"
  aria-hidden="true"
></span>

<style>
  .notification__icon {
    line-height: 2rem;
  }
</style>
