import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import FollowupParentItemDetail from '$lib/components/followup/FollowupParentItemDetail.svelte';
import { FollowupItem, FollowupItemEvent, FollowupSubItem } from '$lib/followup';

vi.mock('$lib/components/followup/FollowupItemDetailHeader.svelte', () => ({
  default: vi.fn(() => ({})),
}));

import FollowupItemDetailHeader from '$lib/components/followup/FollowupItemDetailHeader.svelte';

describe('/FollowupParentItemDetail.svelte', () => {
  beforeEach(() => {
    vi.mocked(FollowupItemDetailHeader).mockClear();
  });

  test('Should use FollowupItemDetailHeader component', async () => {
    // Given
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
      'ref1',
      'notifications',
      [],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'New',
      false,
      'link1',
      []
    );

    // When
    render(FollowupParentItemDetail, { props: { item: item } });

    // Then
    expect(FollowupItemDetailHeader).toHaveBeenCalled();
    expect(FollowupItemDetailHeader).toHaveBeenCalledWith(expect.anything(), {
      item: item,
    });
  });
  test('Should not list events', async () => {
    // Given
    const event1 = new FollowupItemEvent(
      'event-id1',
      new Date('2026-02-03T08:05:42Z'),
      'lorem ipsum 1'
    );
    const event2 = new FollowupItemEvent(
      'event-id2',
      new Date('2026-02-03T09:05:42Z'),
      'lorem ipsum 2'
    );
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
      'ref1',
      'notifications',
      [event2, event1],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'New',
      false,
      'link1',
      []
    );

    // When
    render(FollowupParentItemDetail, { props: { item: item } });

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('item-events-list')).toBeNull();
    });
  });
  test('Should list sub items', async () => {
    // Given
    vi.stubEnv('TZ', 'Europe/Paris');
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
      'ref1',
      'notifications',
      [],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'New',
      false,
      'link1',
      [
        new FollowupSubItem(
          'partner',
          'type',
          'id3',
          'ref3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          true,
          'link3'
        ),
        new FollowupSubItem(
          'partner',
          'type',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          true,
          'link2'
        ),
      ]
    );

    // When
    render(FollowupParentItemDetail, { props: { item: item } });

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('followup-subitems')).not.toBeNull();
      expect(screen.getByTestId('followup-subitems')).toHaveTextContent(
        'Nouveau 22 février 2026 - 16:55 Opération Tranquillité Vacances Votre demande est en cours de traitement 1.Nouveau 22 février 2026 - 16:55 Opération Tranquillité Vacances Votre demande est en cours de traitement 1.'
      );
    });
  });
  test('should display links to subitems', async () => {
    // Given
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
      'ref1',
      'notifications',
      [],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'New',
      false,
      'link1',
      [
        new FollowupSubItem(
          'partner',
          'type',
          'id3',
          'ref3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          true,
          'link3'
        ),
        new FollowupSubItem(
          'partner',
          'type',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          true,
          'link2'
        ),
      ]
    );
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(FollowupParentItemDetail, { props: { item: item } });

    // Then
    expect(
      screen.queryByTestId('followup-subitem-link-partner:type:id3')
    ).toBeInTheDocument();
    expect(
      screen.queryByTestId('followup-subitem-link-partner:type:id2')
    ).toBeInTheDocument();
    const button = screen.getByTestId('followup-subitem-link-partner:type:id3');
    await fireEvent.click(button);
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith(
        '/#/followup/item/partner/type/id1/subitem/partner/type/id3'
      );
    });
  });
});
