import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test } from 'vitest';
import FollowupItemMessages from '$lib/components/followup/FollowupItemMessages.svelte';
import { FollowupItem, FollowupItemEvent } from '$lib/followup';

describe('/FollowupItemMessages.svelte', () => {
  test('Should not list events', async () => {
    // Given
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
      'ref1',
      'notifications',
      null,
      null,
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
    render(FollowupItemMessages, { props: { item: item, displayTitle: true } });

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('item-events-list')).toBeNull();
    });
  });
  test('Should list events', async () => {
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
      null,
      null,
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
    render(FollowupItemMessages, { props: { item: item, displayTitle: true } });

    // Then
    await waitFor(() => {
      expect(screen.getByTestId('item-events-list')).toHaveTextContent(
        '03 février 2026 - 10:05 lorem ipsum 203 février 2026 - 09:05 lorem ipsum 1'
      );
    });
  });
});
