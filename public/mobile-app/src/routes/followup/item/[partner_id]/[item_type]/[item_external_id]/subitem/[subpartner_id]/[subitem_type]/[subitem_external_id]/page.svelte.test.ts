import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { FollowupItem, FollowupSubItem } from '$lib/followup';
import { Services } from '$lib/services';
import Page from './+page.svelte';

vi.mock('$lib/components/followup/FollowupItemDetail.svelte', () => ({
  default: vi.fn(() => ({})),
}));

import FollowupItemDetail from '$lib/components/followup/FollowupItemDetail.svelte';

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.mocked(FollowupItemDetail).mockClear();
  });

  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const sub_item = new FollowupSubItem(
      'subpartner',
      'subtype',
      'subid',
      'ref',
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
      null,
      [sub_item]
    );
    const services = new Services();
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
      subpartner_id: 'subpartner',
      subitem_type: 'subtype',
      subitem_external_id: 'subid',
    };

    // When
    render(Page, { props: { data: { item, sub_item, services }, params: params } });

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
      null,
      null,
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
      [sub_item]
    );
    const services = new Services();
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
      subpartner_id: 'subpartner',
      subitem_type: 'subtype',
      subitem_external_id: 'subid',
    };
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, { props: { data: { item, sub_item, services }, params: params } });
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
      null,
      null,
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
      true,
      'link1',
      [sub_item]
    );
    const services = new Services();
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
      subpartner_id: 'subpartner',
      subitem_type: 'subtype',
      subitem_external_id: 'subid',
    };

    // When
    render(Page, { props: { data: { item, sub_item, services }, params: params } });

    // Then
    expect(FollowupItemDetail).toHaveBeenCalled();
    expect(FollowupItemDetail).toHaveBeenCalledWith(expect.anything(), {
      item: sub_item,
      parentItem: item,
      services: services,
    });
  });
});
