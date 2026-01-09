<script lang="ts">
  import { onMount } from 'svelte'
  import { Item } from '$lib/agenda'

  interface Props {
    item: Item
    // Only display the date on the agenda's page, not on the homepage
    displayDate?: boolean
  }
  let { item, displayDate = true }: Props = $props()
  let agendaItemDate: string = $state('')

  onMount(async () => {
    agendaItemDate = item.date ? item.date.toLocaleDateString('sv-SE') : ''
  })
</script>

<div class="agenda--item">
  {#if displayDate}
    <div class="agenda--item--date">
      <span class="day-name"
        ><span aria-hidden="true">{item.dayName}</span><span class="fr-sr-only"
          >{item.fullDayName}</span
        ></span
      > <span class="day-num">{item.dayNum}</span> 
    </div>
  {/if}
  <div
    class="agenda--item--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link {item.custom ? 'custom': ''} {item.link ? '': 'no-link'}"
  >
    <div class="fr-tile__body">
      <div class="fr-tile__content {item.link ? '': 'no-link'}">
        <h3 class="fr-tile__title">
          <a
            href="{item.link}?date={agendaItemDate}"
            onclick={(e) => {if (!item.link) {e.preventDefault();}}}
            data-testid="agenda-item-link"
            class="{item.link ? '': 'no-link'}"
          >
            {item.title}
          </a>
        </h3>
        {#if item.description}
          <p class="fr-tile__detail">{item.description}</p>
        {/if}
        <div class="fr-tile__start">
          {#if item.custom}
            <p class="fr-badge fr-badge--icon-left fr-icon-user-fill custom"></p>
          {/if}
          <p class="fr-badge fr-badge--icon-left {item.icon} {item.kind}">
            {item.label}
          </p>
          <p class="fr-tag">{item.period}</p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .agenda--item {
    display: flex;
    margin-bottom: 0.75rem;
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
      padding: 1.5rem;
      padding-bottom: 1rem;
      width: 100%;
      &.custom {
        background-image:
          linear-gradient(
            0deg,
            var(--border-default-blue-france),
            var(--border-default-blue-france)
          ),
          linear-gradient(
            0deg,
            var(--border-default-blue-france),
            var(--border-default-blue-france)
          ),
          linear-gradient(
            0deg,
            var(--border-default-blue-france),
            var(--border-default-blue-france)
          ),
          linear-gradient(
            0deg,
            var(--border-default-blue-france),
            var(--border-default-blue-france)
          );
      }
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
          &.custom {
            color: #fff;
            margin-right: 0.25rem;
            background: var(--blue-france-main-525);
            &::before {
              margin-right: 0;
            }
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
