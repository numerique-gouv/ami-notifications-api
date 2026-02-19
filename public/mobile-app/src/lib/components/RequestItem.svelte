<script lang="ts">
  import { onMount } from 'svelte'
  import { RequestItem } from '$lib/follow-up'

  interface Props {
    item: RequestItem
  }
  let { item }: Props = $props()
</script>

<div class="request--item">
  <div
    class="request--item--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link no-link"
  >
    <div class="fr-tile__body">
      <div class="fr-tile__content no-link">
        <h3 class="fr-tile__title">
          <a
            href="#"
            onclick={(e) => {e.preventDefault()}}
            data-testid="request-item-link"
            class="no-link"
          >
            {item.title}
          </a>
        </h3>
        <p class="fr-tile__detail">{item.description}</p>
        <div class="fr-tile__start">
          <p class="fr-badge fr-badge--icon-left {item.icon} {item.status_id}">
            {item.status_label}
          </p>
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
        .fr-badge {
          font-size: 12px;
          font-weight: 700;
          line-height: 20px;
          margin-bottom: 0.5rem;
          &::before {
            --icon-size: 0.75rem;
          }
          &.new {
            color: var(--info-425-625);
            background-color: var(--info-950-100);
          }
          &.wip {
            color: var(--yellow-tournesol-sun-407-moon-922);
            background-color: var(--yellow-tournesol-950-100);
          }
          &.closed {
            color: var(--success-425-625);
            background-color: var(--success-950-100);
          }
        }
      }
    }
  }
</style>
