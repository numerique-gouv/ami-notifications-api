<script lang="ts">
  import DOMPurify from 'dompurify';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { Item } from '$lib/agenda';

  interface Props {
    item: Item;
    // Only display the date on the agenda's page, not on the homepage
    displayDate?: boolean;
    onOpen: () => void;
  }
  let { item, displayDate = true, onOpen }: Props = $props();

  const badgeKinds = {
    otv: 'fr-badge--green-archipel',
    election: 'fr-badge--green-tilleul-verveine',
    holiday: 'am-badge-blue',
  };
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
      class="agenda--item--detail fr-tile fr-tile--sm fr-tile--horizontal fr-enlarge-button {item.link ? '': 'no-link'}"
    >
      <button
        type="button"
        onclick={onOpen}
        data-testid="open-agenda-item-modal-{item.id}"
        class="fr-btn fr-btn--icon fr-icon-more-2-fill fr-btn--tertiary-no-outline fr-pt-2w am-icon-20 am-btn-modal open-agenda-item-modal"
      >
        Ouvrir la modale liée à l'élément de l'agenda
      </button>
      <div class="fr-tile__body">
        <div class="fr-tile__content fr-pb-0 {item.link ? '': 'no-link'}">
          <h4 class="fr-tile__title">
            <button
              type="button"
              onclick={(e) => {if (item.link) { goto(item.link) } else {e.preventDefault();} }}
              data-testid="agenda-item-link"
              class="{item.link ? '': 'no-link'}"
            >
              {item.title}
            </button>
          </h4>
          {#if item.subitems.length == 1}
            {#if item.description}
              <p class="fr-tile__detail fr-text--sm fr-m-0 fr-pr-0">
                {@html DOMPurify.sanitize(item.description)}
              </p>
            {/if}
            <div class="fr-tile__start fr-mb-3v">
              <p
                class="fr-badge fr-badge--sm fr-badge--icon-left fr-mb-1w {item.icon} {badgeKinds[item.kind]}"
              >
                {item.label}
              </p>
              <p class="fr-tag fr-tag--sm">{item.period}</p>
            </div>
          {:else}
            <div class="fr-tile__start fr-mb-3v">
              <p
                class="fr-badge fr-badge--sm fr-badge--icon-left fr-mb-1w {item.icon} {badgeKinds[(item.kind)]} fr-mb-0"
              >
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
          class="agenda--item--detail fr-tile fr-tile--sm fr-tile--horizontal fr-tile--no-icon {item.link ? '': 'no-link'}"
        >
          <div class="fr-tile__body">
            <div class="fr-tile__content  {item.link ? '': 'no-link'}">
              <p class="fr-tile__detail fr-text--sm fr-m-0">
                {@html DOMPurify.sanitize(subitem.description || '')}
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
      color: var(--text-default-grey);
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

      button.am-btn-modal {
        z-index: 2;
        position: absolute;
        top: 1px;
        right: 1px;
        min-height: 3rem;
        outline-width: 2px;

        &:before {
          position: relative;
          width: var(--icon-size);
          height: var(--icon-size);
        }
      }
      .agenda--item--detail {
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
        .fr-tile__content {
          .fr-tile__title {
            &::before {
              background: none;
            }
            button {
              &:before {
                background: none;
              }
              &:after {
                bottom: 0.5rem;
                right: 0.75rem;
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
          .fr-tag {
            display: block;
          }
        }
      }
    }
  }
</style>
