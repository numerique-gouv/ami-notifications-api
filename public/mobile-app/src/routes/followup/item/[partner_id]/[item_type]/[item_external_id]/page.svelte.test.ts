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
      []
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
    };

    // When
    render(Page, { props: { data: { item }, params: params } });

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });
  test('should navigate to /followup on click on back button when item is not archived', async () => {
    // Given
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
      []
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
    };
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page, { props: { data: { item }, params: params } });
    const backButton = screen.getByTestId('back-button');
    await fireEvent.click(backButton);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/followup');
    });
  });
  test('should navigate to /followup/archived on click on back button when item is archived', async () => {
    // Given
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
      []
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
    };
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page, { props: { data: { item }, params: params } });
    const backButton = screen.getByTestId('back-button');
    await fireEvent.click(backButton);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/followup/archived');
    });
  });
  test('should use FollowupItemDetail component as item is not parent', async () => {
    // Given
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
      []
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
    };

    // When
    render(Page, { props: { data: { item }, params: params } });

    // Then
    expect(FollowupItemDetail).toHaveBeenCalled();
    expect(FollowupItemDetail).toHaveBeenCalledWith(expect.anything(), { item: item });
    expect(FollowupParentItemDetail).not.toHaveBeenCalled();
  });
  test('should use FollowupParentItemDetail component as item is parent', async () => {
    // Given
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
      [
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
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
    };

    // When
    render(Page, { props: { data: { item }, params: params } });

    // Then
    expect(FollowupItemDetail).not.toHaveBeenCalled();
    expect(FollowupParentItemDetail).toHaveBeenCalled();
    expect(FollowupParentItemDetail).toHaveBeenCalledWith(expect.anything(), {
      item: item,
    });
  });
});
