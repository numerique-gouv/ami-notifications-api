import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import { FollowupItem, FollowupSubItem } from '$lib/followup';
import Page from './+page.svelte';

vi.mock('$lib/components/FollowupItemDetail.svelte', () => ({
  default: vi.fn(() => ({})),
}));
vi.mock('$lib/components/FollowupParentItemDetail.svelte', () => ({
  default: vi.fn(() => ({})),
}));

import FollowupItemDetail from '$lib/components/FollowupItemDetail.svelte';
import FollowupParentItemDetail from '$lib/components/FollowupParentItemDetail.svelte';

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.mocked(FollowupItemDetail).mockClear();
    vi.mocked(FollowupParentItemDetail).mockClear();
  });

  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();
    const sub_item = new FollowupSubItem(
      'subpartner',
      'subtype',
      'subid',
      'ref',
      'notifications',
      [],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'new',
      false,
      null
    );
    const item = new FollowupItem(
      'partner',
      'type',
      'id',
      'ref',
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
      null,
      [sub_item]
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
      subpartner_id: 'subpartner',
      subitem_type: 'subtype',
      subitem_external_id: 'subid',
    };

    // When
    render(Page, { props: { data: { item, sub_item }, params: params } });

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });
  test('should navigate to item detail page on click on back button', async () => {
    // Given
    const sub_item = new FollowupSubItem(
      'subpartner',
      'subtype',
      'subid',
      'ref',
      'notifications',
      [],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'new',
      false,
      null
    );
    const item = new FollowupItem(
      'partner',
      'type',
      'id',
      'ref',
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
      [sub_item]
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
      subpartner_id: 'subpartner',
      subitem_type: 'subtype',
      subitem_external_id: 'subid',
    };
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page, { props: { data: { item, sub_item }, params: params } });
    const backButton = screen.getByTestId('back-button');
    await fireEvent.click(backButton);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/followup/item/partner/type/id');
    });
  });
  test('should use FollowupItemDetail component', async () => {
    // Given
    const sub_item = new FollowupSubItem(
      'subpartner',
      'subtype',
      'subid',
      'ref',
      'notifications',
      [],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'new',
      false,
      null
    );
    const item = new FollowupItem(
      'partner',
      'type',
      'id',
      'ref',
      'notifications',
      [],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'New',
      true,
      'link1',
      [sub_item]
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
      subpartner_id: 'subpartner',
      subitem_type: 'subtype',
      subitem_external_id: 'subid',
    };

    // When
    render(Page, { props: { data: { item, sub_item }, params: params } });

    // Then
    expect(FollowupItemDetail).toHaveBeenCalled();
    expect(FollowupItemDetail).toHaveBeenCalledWith(expect.anything(), {
      item: sub_item,
    });
    expect(FollowupParentItemDetail).not.toHaveBeenCalled();
  });
});
