<script lang="ts">
  import DOMPurify from 'dompurify';
  import { onMount } from 'svelte';
  import { Item } from '$lib/agenda';

  interface Props {
    item: Item;
    // Only display the date on the agenda's page, not on the homepage
    displayDate?: boolean;
    onOpen: () => void;
  }
  let { item, displayDate = true, onOpen }: Props = $props();
</script>

<div class="agenda--item">
  {#if displayDate}
    <div class="agenda--item--date">
      <span class="day-name">
        <span aria-hidden="true">{item.dayName}</span><span class="fr-sr-only"
          >{item.fullDayName}</span
        >
      </span>
      <span class="day-num">{item.dayNum}</span> 
    </div>
  {/if}
  <div class="agenda--item--container">
    <div
      class="agenda--item--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link {item.link ? '': 'no-link'}"
    >
      <button
        type="button"
        onclick={onOpen}
        data-testid="open-agenda-item-modal-{item.id}"
        class="fr-btn fr-btn--icon fr-icon-more-2-fill fr-btn--tertiary-no-outline fr-pt-2w am-icon-20 open-agenda-item-modal"
      >
        Ouvrir la modale liée à l'élément de l'agenda
      </button>
      <div class="fr-tile__body">
        <div class="fr-tile__content {item.link ? '': 'no-link'}">
          <h4 class="fr-tile__title">
            <a
              href="{item.link}"
              onclick={(e) => {if (!item.link) {e.preventDefault();}}}
              data-testid="agenda-item-link"
              class="{item.link ? '': 'no-link'}"
            >
              {item.title}
            </a>
          </h4>
          {#if item.subitems.length == 1}
            {#if item.description}
              <p class="fr-tile__detail">
                <span>{@html DOMPurify.sanitize(item.description)}</span>
              </p>
            {/if}
            <div class="fr-tile__start">
              <p class="fr-badge fr-badge--icon-left {item.icon} {item.kind}">
                {item.label}
              </p>
              <p class="fr-tag">{item.period}</p>
            </div>
          {:else}
            <div class="fr-tile__start">
              <p class="fr-badge fr-badge--icon-left {item.icon} {item.kind} multitile">
                {item.label}
              </p>
            </div>
          {/if}
        </div>
      </div>
    </div>
    {#if item.subitems.length > 1}
      {#each item.subitems as subitem}
        <div
          class="agenda--item--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link {item.link ? '': 'no-link'}"
        >
          <div class="fr-tile__body">
            <div class="fr-tile__content {item.link ? '': 'no-link'}">
              <p class="fr-tile__detail">
                <span>{@html DOMPurify.sanitize(subitem.description || '')}</span>
              </p>
              <div class="fr-tile__start">
                <p class="fr-tag">{subitem.period}</p>
              </div>
            </div>
          </div>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .agenda--item {
    display: flex;
    &:not(:last-child) {
      margin-bottom: 0.75rem;
    }
    .agenda--item--date {
      display: flex;
      flex-direction: column;
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
    .agenda--item--container {
      display: flex;
      flex-direction: column;
      width: 100%;
      .agenda--item--detail.fr-enlarge-link {
        padding: 1rem 2rem 0.5rem 1rem;
        width: 100%;
        &:not(:first-child) {
          background-image:
            linear-gradient(
              0deg,
              var(--border-default-grey),
              var(--border-default-grey)
            ),
            linear-gradient(
              0deg,
              var(--border-default-grey),
              var(--border-default-grey)
            ),
            linear-gradient(
              0deg,
              var(--border-default-grey),
              var(--border-default-grey)
            ),
            none;
        }
        &.no-link {
          --hover: transparent;
        }
        button.open-agenda-item-modal {
          z-index: 2;
          position: absolute;
          top: 1px;
          right: 1px;
          min-height: 3rem;
        }
        .fr-tile__content {
          padding-bottom: 0;
          .fr-tile__title {
            font-size: 16px;
            &::before {
              background: none;
            }
            a {
              &::before {
                background: none;
              }
              &::after {
                bottom: 0.5rem;
                right: 0.5rem;
                --icon-size: 1.25rem;
                -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
                mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
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
            padding-right: 0;
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
            &.election {
              color: var(--text-action-high-green-tilleul-verveine);
              background-color: var(--background-contrast-green-tilleul-verveine);
            }
            &.multitile {
              margin-bottom: 0;
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
  }
</style>
