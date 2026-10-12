<script lang="ts">
  import DOMPurify from 'dompurify';
  import { onMount } from 'svelte';
  import { Item } from '$lib/agenda';
  import { AMIBackOrGoto, AMIGoto } from '$lib/ami-navigation';
  import { getDSFRIcon } from '$lib/dsfr-icon';
  import { ariaHideDecorativeEmoji } from '$lib/emoji';
  import { FollowupSubItem } from '$lib/followup';

  interface Props {
    item: Item;
    // Only display the date on the agenda's page, not on the homepage
    displayDate?: boolean;
    displayDay?: boolean;
    Date?: boolean;
    isPast?: boolean;
    followupSubItem?: FollowupSubItem | null;
    useBackOrGoto?: boolean;
    hasModal?: boolean;
    index?: string;
  }
  let {
    item,
    displayDate = true,
    displayDay = true,
    isPast = false,
    followupSubItem = null,
    useBackOrGoto = false,
    hasModal = false,
    index = '',
  }: Props = $props();

  let checkedIcon = '';
  if (followupSubItem) {
    checkedIcon = getDSFRIcon(followupSubItem.icon, 'fr-icon-information-fill');
  }

  const goToItem = (event: Event) => {
    if (item.link) {
      if (useBackOrGoto) {
        AMIBackOrGoto(item.link);
        return;
      }
      AMIGoto(item.link);
      return;
    }
    event.preventDefault();
  };
</script>

<div class="agenda--item">
  {#if displayDate}
    <div class="agenda--item--date">
      {#if displayDay}
        <h3 class="fr-sr-only">{item.fullDayName} {item.dayNum} {item.monthName}</h3>
        <span aria-hidden="true" class="day-name">{item.dayName}</span>
        <span aria-hidden="true" class="day-num">{item.dayNum}</span>
      {/if}
    </div>
  {/if}
  <div class="agenda--item--container">
    <div
      class="fr-card fr-enlarge-button fr-card--sm fr-card--horizontal agenda--item--detail
              {item.kind}
              {isPast ? 'past': ''}
              {item.link ? '': 'fr-card--no-icon no-link'}
              {hasModal ? '': 'am-without-opt'}
      "
    >
      {#if hasModal}
        <button
          data-fr-opened="false"
          aria-controls="agenda-item-{index}-modal"
          id="agenda-item-{item.key}-button"
          type="button"
          data-testid="agenda-item-{item.key}-open-modal-button"
          class="fr-btn fr-btn--icon fr-icon-more-2-fill fr-btn--tertiary-no-outline fr-pt-2w am-icon-20 am-btn-modal open-agenda-item-modal"
        >
          Ouvrir les options pour {item.title}
        </button>
      {/if}
      <div class="fr-card__body fr-p-0">
        <div class="fr-card__content fr-m-0 fr-pb-3v">
          <h4 class="fr-card__title fr-text--md">
            <button type="button" onclick={goToItem} data-testid="agenda-item-link">
              {@html ariaHideDecorativeEmoji(item.title)}
            </button>
          </h4>
          {#if item.subitems.length == 1}
            {#if item.description}
              <p class="fr-card__desc fr-text--sm fr-mt-1w">
                {@html ariaHideDecorativeEmoji(DOMPurify.sanitize(item.description), false)}
              </p>
            {/if}
            <div class="fr-card__start fr-mb-0">
              {#if followupSubItem}
                <div>
                  <p
                    class="fr-badge fr-mb-1w fr-badge--icon-left {checkedIcon} {followupSubItem.status_id} {followupSubItem.badgeClassName}"
                  >
                    {followupSubItem.status_label}
                  </p>
                </div>
              {/if}
              <p
                class="fr-badge fr-badge--sm fr-badge--icon-left fr-mb-1w fr-mr-1v {item.icon} {item.badgeClassName}"
              >
                {item.period}
              </p>
            </div>
          {/if}
        </div>
      </div>
    </div>
    {#if item.subitems.length > 1}
      <div class="agenda--subitems">
        {#each item.subitems as subitem}
          <div
            class="fr-card fr-card--sm fr-card--horizontal fr-card--no-icon agenda--item--detail {item.link ? '': 'no-link'} "
          >
            <div class="fr-card__body fr-p-0">
              <div class="fr-card__content fr-m-0 fr-pb-3v fr-pr-2w">
                <p class="fr-card__desc fr-text--sm fr-m-0">
                  {@html ariaHideDecorativeEmoji(DOMPurify.sanitize(subitem.description || ''), false)}
                </p>
                <div
                  class="fr-card__start fr-mb-0"
                  class:with-personal-icon={subitem.isPersonal}
                >
                  <p
                    class="fr-badge fr-badge--sm fr-badge--icon-left fr-mb-1w {item.icon} {item.badgeClassName}"
                  >
                    {subitem.period}
                  </p>
                  {#if subitem.isPersonal}
                    <p
                      class="fr-badge fr-badge--sm fr-badge--icon-left fr-mb-1w fr-icon-user-fill am-badge--user"
                    >
                      <span class="fr-sr-only">Personel</span>
                    </p>
                  {/if}
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
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
        top: 0;
        right: 0;
        min-height: 2.75rem;
        outline-width: 2px;

        &:before {
          position: relative;
          height: 1.25rem;
        }
      }
    }
    .fr-card {
      width: 100%;
      &.personal:not(.past) {
        background-image:
          linear-gradient(0deg, var(--am-blue--1), var(--am-blue--1)),
          linear-gradient(0deg, var(--am-blue--1), var(--am-blue--1)),
          linear-gradient(0deg, var(--am-blue--1), var(--am-blue--1)),
          linear-gradient(0deg, var(--am-blue--1), var(--am-blue--1));
      }
      &.past {
        background-color: var(--grey-975-75);
        background-image:
          linear-gradient(
            0deg,
            var(--border-contrast-grey),
            var(--border-contrast-grey)
          ),
          linear-gradient(
            0deg,
            var(--border-contrast-grey),
            var(--border-contrast-grey)
          ),
          linear-gradient(
            0deg,
            var(--border-contrast-grey),
            var(--border-contrast-grey)
          ),
          linear-gradient(
            0deg,
            var(--border-contrast-grey),
            var(--border-contrast-grey)
          );
      }
      &.no-link {
        --hover: transparent;
        --active: transparent;
      }
      .fr-card__content {
        padding: 0.875rem 2rem 0.875rem 1rem;
      }
    }
    .fr-card--sm.fr-enlarge-button:not(.fr-card--no-icon) .fr-card__title button:after {
      bottom: 0.5rem;
      right: 0.75rem;
      --icon-size: 1.25rem;
      -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
      mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
    }

    .fr-card--sm.am-without-opt.fr-enlarge-button:not(.fr-card--no-icon)
      .fr-card__title
      button:after {
      bottom: 50%;
      transform: translateY(50%);
    }
    .fr-card__start.with-personal-icon {
      display: flex;
      justify-content: space-between;
      gap: 0.5rem;
      width: 100%;

      .fr-icon-user-fill.am-badge--user {
        max-height: 1.25rem;
        padding: 0 0.25rem;
        &::before {
          margin: 0;
        }
      }
    }
  }
  .agenda--subitems {
    border-left: solid 1px var(--border-default-grey);
    border-right: solid 1px var(--border-default-grey);
    .fr-card {
      z-index: 1;
      background-image: none;
      width: calc(100% + 2px);
      margin: 0 -1px;
      border: solid 1px var(--border-default-grey);
      border-top: none;
      &:not(:last-child) {
        border-radius: 0 0 0.5rem 0.5rem;
      }
    }
  }
</style>
