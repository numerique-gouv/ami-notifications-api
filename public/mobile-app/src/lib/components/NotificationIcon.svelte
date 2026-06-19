<script lang="ts">
  import { getDSFRIcon } from '$lib/dsfr-icon';

  interface Props {
    defaultIcon: string;
    icon?: string;
  }
  let { defaultIcon, icon = '' }: Props = $props();

  let checkedIcon = $derived(getDSFRIcon(icon, defaultIcon));
</script>

<span class="notification__icon {checkedIcon}" aria-hidden="true"></span>

<style>
  .notification__icon {
    line-height: 2rem;
    color: var(--blue-france-sun-113-625);
    &::before {
      --icon-size: 1.25rem;
    }
  }
</style>
