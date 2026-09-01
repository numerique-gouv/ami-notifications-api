<script lang="ts">
  import { goto } from '$app/navigation';
  import FollowupItemDetailHeader from '$lib/components/followup/FollowupItemDetailHeader.svelte';
  import { getDSFRIcon } from '$lib/dsfr-icon';
  import { FollowupItem } from '$lib/followup';

  interface Props {
    item: FollowupItem;
  }
  let { item }: Props = $props();

  let checkedIcon = $derived(getDSFRIcon(item.icon, 'fr-icon-information-fill'));

  const gotoExternalItem = () => {
    if (item?.link) {
      window.location.href = item.link;
    }
  };
</script>

<div class="demarche-content-container">
  <FollowupItemDetailHeader item={item} />

  <nav class="fr-sidemenu fr-m-0 followup--subitems" data-testid="followup-subitems">
    <div class="fr-sidemenu__inner">
      <ul class="fr-sidemenu__list">
        {#each item.sub_items as sub_item}
          <li class="fr-sidemenu__item followup--subitem fr-py-1w fr-pr-7v">
            <div class="followup--subitem__header fr-mb-1v">
              <p
                class="fr-badge fr-badge--sm fr-badge--icon-left {checkedIcon} {sub_item.status_id} {sub_item.badgeClassName} fr-mr-3v"
              >
                {sub_item.status_label}
              </p>
              <p
                class="fr-text--regular fr-text--xs am-text-mention-grey followup--subitem__date"
              >
                {sub_item.formattedDate}
              </p>
            </div>
            <button
              type="button"
              class="fr-sidemenu__btn fr-text--sm fr-p-0"
              onclick={(e) => goto(sub_item.getItemDetailPageUrl(item))}
              data-testid="followup-subitem-link-{sub_item.id}"
            >
              {sub_item.title}
            </button>
            <p
              class="fr-text--regular fr-text--xs fr-m-0"
              data-testid="followup-subitem-detail-{sub_item.id}"
            >
              {sub_item.description}
            </p>
          </li>
        {/each}
      </ul>
    </div>
  </nav>
</div>

<style>
  div.demarche-content-container {
    padding: 4rem 1rem 1rem;
    .followup--subitem__header {
      display: flex;
      justify-content: space-between;
      .fr-badge {
        display: inline-block;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
      }
      .followup--subitem__date {
        flex-shrink: 0;
      }
    }
    .fr-sidemenu {
      box-shadow: none;
    }
    .fr-sidemenu__btn {
      display: block;
      position: initial;
      &:before {
        position: absolute;
        content: "";
        display: block;
        bottom: 0;
        height: 100%;
        left: 0;
        outline-color: inherit;
        outline-offset: 2px;
        outline-style: inherit;
        outline-width: 2px;
        right: 0;
        top: 0;
        width: 100%;
        z-index: 1;
      }
      &:after {
        position: absolute;
        content: "";
        display: block;
        height: 1.25rem;
        width: 1.25rem;
        -webkit-mask-size: 100% 100%;
        mask-size: 100% 100%;
        -webkit-mask-image: url("../../../../node_modules/@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
        mask-image: url("../../../../node_modules/@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
        top: 50%;
        right: 0;
        transform: translateY(-50%);
        background-color: var(--text-active-blue-france);
      }
    }
  }
</style>
