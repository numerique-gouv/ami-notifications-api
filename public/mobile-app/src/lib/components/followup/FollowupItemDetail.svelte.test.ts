import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import FollowupItemDetail from '$lib/components/followup/FollowupItemDetail.svelte';
import { FollowupItem, FollowupItemEvent, FollowupSubItem } from '$lib/followup';

vi.mock('$lib/components/followup/FollowupItem.svelte', () => ({
  default: vi.fn(() => ({})),
}));
vi.mock('$lib/components/followup/FollowupItemDetailHeader.svelte', () => ({
  default: vi.fn(() => ({})),
}));

import FollowupItemComponent from '$lib/components/followup/FollowupItem.svelte';
import FollowupItemDetailHeader from '$lib/components/followup/FollowupItemDetailHeader.svelte';

describe('/FollowupItemDetail.svelte', () => {
  beforeEach(() => {
    vi.mocked(FollowupItemDetailHeader).mockClear();
    vi.mocked(FollowupItemComponent).mockClear();
  });

  test('Should use FollowupItemDetailHeader component', async () => {
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
    render(FollowupItemDetail, { props: { item: item } });

    // Then
    await waitFor(() => {
      expect(screen.getByTestId('item-events-list')).toHaveTextContent(
        '03 février 2026 - 10:05 lorem ipsum 203 février 2026 - 09:05 lorem ipsum 1'
      );
    });
  });
  describe('parent item', async () => {
    test('Should list sub items', async () => {
      // Given
      const subitem1 = new FollowupSubItem(
        'partner',
        'type',
        'id3',
        'ref3',
        'notifications',
        null,
        null,
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
      );
      const subitem2 = new FollowupSubItem(
        'partner',
        'type',
        'id2',
        'ref2',
        'notifications',
        null,
        null,
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
      );
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
        [subitem1, subitem2]
      );

      // When
      render(FollowupItemDetail, { props: { item: item } });

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
      const subitem1 = new FollowupSubItem(
        'partner',
        'type',
        'id3',
        'ref3',
        'notifications',
        null,
        null,
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
      );
      const subitem2 = new FollowupSubItem(
        'partner',
        'type',
        'id2',
        'ref2',
        'notifications',
        null,
        null,
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
      );
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
        [subitem1, subitem2]
      );
      const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

      // When
      render(FollowupItemDetail, { props: { item: item } });

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
    test('Should not display link to parent as it is not a child', async () => {
      // Given
      const subitem1 = new FollowupSubItem(
        'partner',
        'type',
        'id3',
        'ref3',
        'notifications',
        null,
        null,
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
      );
      const subitem2 = new FollowupSubItem(
        'partner',
        'type',
        'id2',
        'ref2',
        'notifications',
        null,
        null,
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
      );
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
        [subitem1, subitem2]
      );

      // When
      render(FollowupItemDetail, { props: { item: item } });

      // Then
      await waitFor(() => {
        expect(screen.queryByTestId('followup-parent')).toBeNull();
      });
    });
  });
  describe('sub item', async () => {
    test('Should not list sub items', async () => {
      // Given
      const subitem1 = new FollowupSubItem(
        'partner',
        'type',
        'id3',
        'ref3',
        'notifications',
        null,
        null,
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
      );
      const subitem2 = new FollowupSubItem(
        'partner',
        'type',
        'id2',
        'ref2',
        'notifications',
        null,
        null,
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
      );
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
        [subitem1, subitem2]
      );

      // When
      render(FollowupItemDetail, { props: { item: subitem1, parentItem: item } });

      // Then
      await waitFor(() => {
        expect(screen.queryByTestId('followup-subitems')).toBeNull();
      });
    });
    test('Should not display link to parent as it is a sub item without milestone', async () => {
      // Given
      const subitem1 = new FollowupSubItem(
        'partner',
        'type',
        'id3',
        'ref3',
        'notifications',
        null,
        null,
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
      );
      const subitem2 = new FollowupSubItem(
        'partner',
        'type',
        'id2',
        'ref2',
        'notifications',
        null,
        null,
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
      );
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
        [subitem1, subitem2]
      );
      vi.spyOn(subitem1, 'hasMilestone').mockReturnValue(false);

      // When
      render(FollowupItemDetail, { props: { item: subitem1, parentItem: item } });

      // Then
      await waitFor(() => {
        expect(screen.queryByTestId('followup-parent')).toBeNull();
      });
    });
    test('Should display link to parent as it is a sub item with milestone', async () => {});
    // Given
    const subitem1 = new FollowupSubItem(
      'partner',
      'type',
      'id3',
      'ref3',
      'notifications',
      null,
      null,
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
    );
    const subitem2 = new FollowupSubItem(
      'partner',
      'type',
      'id2',
      'ref2',
      'notifications',
      null,
      null,
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
    );
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
      [subitem1, subitem2]
    );
    vi.spyOn(subitem1, 'hasMilestone').mockReturnValue(true);

    // When
    render(FollowupItemDetail, { props: { item: subitem1, parentItem: item } });

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('followup-parent')).not.toBeNull();
      expect(FollowupItemComponent).toHaveBeenCalled();
      expect(FollowupItemComponent).toHaveBeenCalledWith(expect.anything(), {
        item: item,
      });
    });
  });
});
