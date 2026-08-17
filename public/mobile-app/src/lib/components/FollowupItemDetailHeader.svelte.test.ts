import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import FollowupItemDetailHeader from '$lib/components/FollowupItemDetailHeader.svelte';
import { FollowupItem } from '$lib/followup';

describe('/FollowupItemDetailHeader.svelte', () => {
  test('Should display subheading', async () => {
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
    render(FollowupItemDetailHeader, { props: { item: item } });

    // Then
    await waitFor(() => {
      expect(screen.getByTestId('item-subheading')).toHaveTextContent('subheading');
    });
  });
  test('Should not display subheading as it is not defined', async () => {
    // Given
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
      'ref1',
      'notifications',
      [],
      'title',
      '',
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
    render(FollowupItemDetailHeader, { props: { item: item } });

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('item-subheading')).toBeNull();
    });
  });
  test('Should display reference', async () => {
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
    render(FollowupItemDetailHeader, { props: { item: item } });

    // Then
    await waitFor(() => {
      expect(screen.getByTestId('item-reference')).toHaveTextContent(
        'référence dossier : ref1'
      );
    });
  });
  test('Should not display reference as it is undefined', async () => {
    // Given
    const item = new FollowupItem(
      'partner',
      'type',
      'id1',
      '',
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
    render(FollowupItemDetailHeader, { props: { item: item } });

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('item-reference')).toBeNull();
    });
  });
  test('Should display "Accéder à ma démarche" button', async () => {
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
    vi.stubGlobal('location', { href: 'fake-link' });

    // When
    render(FollowupItemDetailHeader, { props: { item: item } });
    await waitFor(async () => {
      expect(screen.queryByTestId('external-item-button')).not.toBeNull();
    });
    const button = screen.getByTestId('external-item-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(window.location.href).toBe('link1');
    });
  });
  test('Should not display "Accéder à ma démarche" button as link is not defined', async () => {
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
      '',
      []
    );
    vi.stubGlobal('location', { href: 'fake-link' });

    // When
    render(FollowupItemDetailHeader, { props: { item: item } });
    await waitFor(async () => {
      expect(screen.queryByTestId('external-item-button')).toBeNull();
    });
  });
});
