<script lang="ts">
  import dsfrIconList from '@gouvfr/dsfr/.config/icon.json';
  import { onMount } from 'svelte';

  interface Props {
    defaultIcon: string;
    icon?: string;
  }
  let { defaultIcon, icon = '' }: Props = $props();
  let checkedIcon: string = $state('');

  onMount(async () => {
    checkedIcon = dsfrIconList.filter((i) => i.name === icon?.replace('fr-icon-', ''))
      .length
      ? icon
      : defaultIcon;
  });
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
