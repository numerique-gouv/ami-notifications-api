import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMIGotoMethods from '$lib/ami-goto';
import { FollowupItem, FollowupItemEvent } from '$lib/followup';
import Page from '$routes/followup/item/[partner_id]/[item_type]/[item_external_id]/+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();
    const event = new FollowupItemEvent(
      'event-id',
      new Date('2026-02-03T08:05:42Z'),
      'lorem ipsum'
    );
    const item = new FollowupItem(
      'partner',
      'type',
      'id',
      'notifications',
      [event],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'New',
      false,
      null
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
      expect(spy).toHaveBeenCalledWith('/');
    });
  });
  test('should navigate to /followup on click on back button when item is not archived', async () => {
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
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
      'link1'
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
    };
    const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

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
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
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
      'link1'
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
    };
    const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, { props: { data: { item }, params: params } });
    const backButton = screen.getByTestId('back-button');
    await fireEvent.click(backButton);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/followup/archived');
    });
  });
  test('Should display "Accéder à ma démarche" button', async () => {
    // Given
    const event = new FollowupItemEvent(
      'event-id',
      new Date('2026-02-03T08:05:42Z'),
      'lorem ipsum'
    );
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
      'notifications',
      [event],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'New',
      false,
      'link1'
    );
    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
    };
    const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, { props: { data: { item }, params: params } });

    // Then
    await waitFor(async () => {
      expect(
        screen.queryByTestId('external-item-button-partner:type:id1')
      ).not.toBeNull();
    });

    // When
    const button = screen.getByTestId('external-item-button-partner:type:id1');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('link1');
    });
  });
});
