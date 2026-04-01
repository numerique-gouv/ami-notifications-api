<script lang="ts">
  import { onMount } from 'svelte';
  import { RequestItem } from '$lib/follow-up';

  interface Props {
    item: RequestItem;
  }
  let { item }: Props = $props();
</script>

<div class="request--item">
  <div
    class="request--item--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link no-link"
  >
    <div class="fr-tile__body">
      <div class="fr-tile__content {item.link ? '': 'no-link'}">
        <h3 class="fr-tile__title">
          <a
            href="{item.link}"
            onclick={(e) => {if (!item.link) {e.preventDefault();}}}
            data-testid="request-item-link"
            class="{item.link ? '': 'no-link'}"
          >
            {item.title}
          </a>
        </h3>
        <p class="fr-tile__detail">{item.description}</p>
        <div class="fr-tile__start">
          <p class="fr-badge fr-badge--icon-left {item.icon} {item.status_id}">
            {item.status_label}
          </p>
          <p class="request--item--detail--date">{item.formattedDate}</p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .request--item {
    display: flex;
    margin-bottom: 0.75rem;
    .request--item--detail {
      padding: 1.5rem;
      padding-bottom: 1rem;
      width: 100%;
      .fr-tile__content {
        padding-bottom: 1.5rem;
        &.no-link {
          padding-bottom: 0;
        }
        .fr-tile__title {
          font-size: 16px;
          a {
            color: var(--text-action-high-blue-france);
            &::after {
              bottom: 1.25rem;
              right: 1.25rem;
              --icon-size: 1rem;
            }
            &.no-link {
              cursor: default;
              &::after {
                display: none;
              }
            }
          }
        }
        .fr-tile__detail {
          font-size: 14px;
          line-height: 24px;
          margin: 0;
        }
        .fr-tile__start {
          width: 100%;
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          .fr-badge {
            font-size: 12px;
            font-weight: 700;
            line-height: 20px;
            margin-bottom: 0.5rem;
            color: var(--info-425-625);
            background-color: var(--info-950-100);
            &::before {
              --icon-size: 0.75rem;
            }
          }
          .request--item--detail--date {
            font-size: 12px;
            line-height: 20px;
            color: var(--text-mention-grey);
          }
        }
      }
    }
  }
</style>
