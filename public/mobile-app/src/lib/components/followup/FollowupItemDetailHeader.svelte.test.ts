import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import FollowupItemDetailHeader from '$lib/components/followup/FollowupItemDetailHeader.svelte';
import { FollowupItem } from '$lib/followup';
import { Services, ServicesItem } from '$lib/services';

describe('/FollowupItemDetailHeader.svelte', () => {
  test('Should display subheading', async () => {
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
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });

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
      null,
      null,
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
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });

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
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });

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
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('item-reference')).toBeNull();
    });
  });
  test('Should not display a period as item has no milestone', async () => {
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
    vi.spyOn(item, 'hasMilestone').mockReturnValue(false);

    // When
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });

    // Then
    expect(screen.queryByTestId('item-period')).toBeNull();
  });
  test('Should display a period', async () => {
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
    vi.spyOn(item, 'hasMilestone').mockReturnValue(true);
    vi.spyOn(item, 'period', 'get').mockReturnValue('A Period');

    // When
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });

    // Then
    const period = screen.getByTestId('item-period');
    expect(period).toHaveTextContent('A Period');
  });
  test('Should not display a duration as item has no milestone', async () => {
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
    vi.spyOn(item, 'hasMilestone').mockReturnValue(false);

    // When
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });

    // Then
    expect(screen.queryByTestId('item-duration')).toBeNull();
  });
  test('Should not display a duration as item has no duration', async () => {
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
    vi.spyOn(item, 'hasMilestone').mockReturnValue(true);
    vi.spyOn(item, 'duration', 'get').mockReturnValue(undefined);

    // When
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });

    // Then
    expect(screen.queryByTestId('item-duration')).toBeNull();
  });
  test('Should display a period', async () => {
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
    vi.spyOn(item, 'hasMilestone').mockReturnValue(true);
    vi.spyOn(item, 'duration', 'get').mockReturnValue('A Duration');

    // When
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });

    // Then
    const duration = screen.getByTestId('item-duration');
    expect(duration).toHaveTextContent('A Duration');
  });
  test('Should display "Accéder à ma démarche" button', async () => {
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
    vi.spyOn(item, 'hasMilestone').mockReturnValue(false);

    // When
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });
    await waitFor(async () => {
      expect(screen.queryByTestId('external-item-button')).not.toBeNull();
    });
    const button = screen.getByTestId('external-item-button');

    // Then
    expect(button).toHaveTextContent('Accéder à ma démarche');
  });
  test('Should display "Accéder au détail du rendez-vous" button', async () => {
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
    vi.spyOn(item, 'hasMilestone').mockReturnValue(true);

    // When
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });
    await waitFor(async () => {
      expect(screen.queryByTestId('external-item-button')).not.toBeNull();
    });
    const button = screen.getByTestId('external-item-button');

    // Then
    expect(button).toHaveTextContent('Accéder au détail du rendez-vous');
  });
  test('Should do a silent login as service is unknown', async () => {
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
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    vi.spyOn(item, 'hasMilestone').mockReturnValue(false);

    // When
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });
    await waitFor(async () => {
      expect(screen.queryByTestId('external-item-button')).not.toBeNull();
    });
    const button = screen.getByTestId('external-item-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('link1', true);
    });
  });
  test('Should do a silent login as service is known and configured with silent login', async () => {
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
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    vi.spyOn(item, 'hasMilestone').mockReturnValue(false);
    const serviceItem = new ServicesItem(
      'partner',
      'type',
      'catalog',
      'title',
      'short description',
      'description',
      'external-url',
      'icon',
      true
    );
    const services = new Services();
    vi.spyOn(services, 'find').mockReturnValue(serviceItem);

    // When
    render(FollowupItemDetailHeader, { props: { item: item, services: services } });
    await waitFor(async () => {
      expect(screen.queryByTestId('external-item-button')).not.toBeNull();
    });
    const button = screen.getByTestId('external-item-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('link1', true);
    });
  });
  test('Should not do a silent login as service is known and configured without silent login', async () => {
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
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    vi.spyOn(item, 'hasMilestone').mockReturnValue(false);
    const serviceItem = new ServicesItem(
      'partner',
      'type',
      'catalog',
      'title',
      'short description',
      'description',
      'external-url',
      'icon',
      false
    );
    const services = new Services();
    vi.spyOn(services, 'find').mockReturnValue(serviceItem);

    // When
    render(FollowupItemDetailHeader, { props: { item: item, services: services } });
    await waitFor(async () => {
      expect(screen.queryByTestId('external-item-button')).not.toBeNull();
    });
    const button = screen.getByTestId('external-item-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('link1', false);
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
      '',
      []
    );
    vi.stubGlobal('location', { href: 'fake-link' });

    // When
    render(FollowupItemDetailHeader, {
      props: { item: item, services: new Services() },
    });
    await waitFor(async () => {
      expect(screen.queryByTestId('external-item-button')).toBeNull();
    });
  });
});
