<script lang="ts">
  import { goto } from '$app/navigation';
  import FollowupItemDetailHeader from '$lib/components/FollowupItemDetailHeader.svelte';
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

  <div class="followup--subitems" data-testid="followup-subitems">
    {#each item.sub_items as sub_item}
      <div class="followup--subitem">
        <div
          class="followup--subitem--detail fr-tile fr-tile--sm fr-tile--horizontal fr-tile--no-border fr-enlarge-button"
        >
          <div class="fr-tile__body">
            <div class="fr-tile__content fr-pb-0">
              <h3 class="fr-tile__title fr-mb-0">
                <button
                  type="button"
                  class="fr-text--sm"
                  onclick={(e) => goto(sub_item.getItemDetailPageUrl(item))}
                  data-testid="followup-subitem-link-{sub_item.id}"
                >
                  {sub_item.title}
                </button>
              </h3>
              <p
                class="fr-tile__detail fr-text--xs fr-m-0 fr-pr-0"
                data-testid="followup-subitem-detail-{sub_item.id}"
              >
                <span> {sub_item.description} </span>
              </p>
              <div class="fr-tile__start fr-mb-1v">
                <p
                  class="fr-badge fr-badge--icon-left {checkedIcon} {sub_item.status_id} am-badge-blue"
                >
                  {sub_item.status_label}
                </p>
                <p class="fr-text--xs followup--subitem--detail--date">
                  {sub_item.formattedDate}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  div.demarche-content-container {
    padding: 4rem 1rem 1rem;
    .followup--subitem {
      display: flex;
      flex-direction: column;
      width: 100%;
      border-bottom: solid 1px var(--border-default-grey);
      .followup--subitem--detail {
        padding: 1rem 1.5rem 1.25rem 0;
        width: 100%;
        .fr-tile__content {
          .fr-tile__title {
            &::before {
              background: none;
            }
            button {
              color: #000;
              &::before {
                background: none;
              }
              &::after {
                top: 50%;
                right: 0;
                --icon-size: 1.25rem;
                -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
                mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
              }
            }
          }
          .fr-tile__start {
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
          }
        }
      }
    }
  }
</style>
