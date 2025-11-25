<script lang="ts">
import { Item } from '$lib/agenda'
interface Props {
  item: Item
}
let { item } = $props<Props>()
</script>

<div class="agenda--item">
  <div class="agenda--item--date">
    <span class="day-name">{item.dayName}</span> 
    <span class="day-num">{item.dayNum}</span> 
  </div>
  <div class="agenda--item--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
    <div class="fr-tile__body">
      <div class="fr-tile__content">
        <h3 class="fr-tile__title">
          <a href="/#/agenda/">{item.title}</a>
        </h3>
        {#if item.description}<p class="fr-tile__detail">{item.description}</p>{/if}
        <div class="fr-tile__start">
          <p class="fr-badge fr-badge--icon-left {item.icon} {item.kind}">
            {item.label}
          </p>
          <p class="fr-tag">
            {item.period}
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .agenda--item {
    display: flex;
    .agenda--item--date {
      width: 2rem;
      color: #000;
      text-align: center;
      margin-right: 1rem;
      .day-name {
        font-size: 12px;
        line-height: 20px;
      }
      .day-num {
        font-size: 16px;
        font-weight: 700;
      }
    }
    .agenda--item--detail {
      margin-bottom: 0.75rem;
      padding: 1.5rem;
      padding-bottom: 1rem;
      width: 100%;
      .fr-tile__content {
        padding-bottom: 1.5rem;
        .fr-tile__title {
          font-size: 16px;
          a::after {
            bottom: 1.25rem;
            right: 1.25rem;
            --icon-size: 1rem;
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
          color: var(--text-active-blue-france);
          background-color: var(--background-action-low-blue-france);
          margin-bottom: 0.5rem;
          &::before {
            --icon-size: 0.75rem;
          }
          &.otv {
            color: var(--text-action-high-green-archipel);
            background-color: var(--background-alt-green-archipel);
          }
        }
        .fr-tag {
          font-size: 12px;
          line-height: 20px;
          min-height: 0;
          display: block;
          padding: 2px 8px;
        }
      }
    }
  }
</style>
