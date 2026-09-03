import { render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import FollowupItemDetail from '$lib/components/followup/FollowupItemDetail.svelte';
import { FollowupItem, FollowupItemEvent, FollowupSubItem } from '$lib/followup';

vi.mock('$lib/components/followup/FollowupItemDetailHeader.svelte', () => ({
  default: vi.fn(() => ({})),
}));

import FollowupItemDetailHeader from '$lib/components/followup/FollowupItemDetailHeader.svelte';

describe('/FollowupItemDetail.svelte', () => {
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
    render(FollowupItemDetail, { props: { item: item } });

    // Then
    expect(FollowupItemDetailHeader).toHaveBeenCalled();
    expect(FollowupItemDetailHeader).toHaveBeenCalledWith(expect.anything(), {
      item: item,
    });
  });
  test('Should list notifications', async () => {
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
    render(FollowupItemDetail, { props: { item: item } });

    // Then
    await waitFor(() => {
      expect(screen.getByTestId('item-events-list')).toHaveTextContent(
        '03 février 2026 - 10:05 lorem ipsum 203 février 2026 - 09:05 lorem ipsum 1'
      );
    });
  });
  test('Should not list sub items', async () => {
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
          'id1',
          'ref1',
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
          'link1'
        ),
        new FollowupSubItem(
          'partner',
          'type',
          'id1',
          'ref1',
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
          'link1'
        ),
      ]
    );

    // When
    render(FollowupItemDetail, { props: { item: item } });

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('followup-subitems')).toBeNull();
    });
  });
});
