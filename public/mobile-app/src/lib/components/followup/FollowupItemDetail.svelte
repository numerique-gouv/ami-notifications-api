<script lang="ts">
  import { AMIGoto } from '$lib/ami-navigation';
  import FollowupItemComponent from '$lib/components/followup/FollowupItem.svelte';
  import FollowupItemDetailHeader from '$lib/components/followup/FollowupItemDetailHeader.svelte';
  import { getDSFRIcon } from '$lib/dsfr-icon';
  import { FollowupItem, FollowupSubItem } from '$lib/followup';

  interface Props {
    item: FollowupSubItem;
    parentItem?: FollowupItem | null;
  }
  let { item, parentItem = null }: Props = $props();
  const displayParent: boolean = $derived(item.hasMilestone() && parentItem !== null);
</script>

<div class="demarche-content-container">
  <FollowupItemDetailHeader item={item} />

  {#if parentItem !== null && displayParent}
    <div class="demarche-content-parent-link fr-mb-3w" data-testid="followup-parent">
      <h2 class="fr-h6 fr-mb-2w">Démarche attachée&nbsp;:</h2>
      <FollowupItemComponent item={parentItem} />
    </div>
  {/if}

  {#if item.events.length}
    <div class="demarche-content-messages">
      <h2 class="fr-h6 fr-mb-0">Messages&nbsp;:</h2>
      <ul class="demarche--events fr-mb-3w fr-raw-list" data-testid="item-events-list">
        {#each item.events as event}
          <li class="fr-py-1w">
            <p
              class="fr-text--sm am-text-mention-grey demarche--events--date fr-m-0 fr-p-0"
            >
              {event.formattedDate}
            </p>
            <p class="fr-text--sm fr-m-0 fr-p-0">{event.description}</p>
          </li>
        {/each}
      </ul>
    </div>
  {/if}

  {#if parentItem === null && (item as FollowupItem).sub_items.length}
    <nav class="fr-sidemenu fr-m-0 followup--subitems" data-testid="followup-subitems">
      <div class="fr-sidemenu__inner">
        <h2 class="fr-h6 fr-mb-0">Sous-démarches associées&nbsp;:</h2>
        <ul class="fr-sidemenu__list fr-mb-3w">
          {#each (item as FollowupItem).sub_items as sub_item}
            <li class="fr-sidemenu__item followup--subitem fr-py-1w fr-pr-7v">
              <div class="followup--subitem__header fr-mb-1v">
                <p
                  class="fr-badge fr-badge--sm fr-badge--icon-left {getDSFRIcon(sub_item.icon, 'fr-icon-information-fill')} {sub_item.status_id} {sub_item.badgeClassName} fr-mr-3v"
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
                onclick={(e) => AMIGoto(sub_item.getItemDetailPageUrl(item as FollowupItem))}
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
  {/if}
</div>

<style>
  div.demarche-content-container {
    padding: 4rem 1rem 1rem;
    div.demarche-content-messages {
      .demarche--events {
        li {
          border-bottom: 1px solid var(--background-alt-grey-active);
        }
      }
    }
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
        -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
        mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
        top: 50%;
        right: 0;
        transform: translateY(-50%);
        background-color: var(--text-active-blue-france);
      }
    }
  }
</style>
