import { render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as consentsMethods from '$lib/consents';
import { Consents } from '$lib/consents';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem } from '$lib/followup';
import { Partners } from '$lib/partners';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  beforeEach(async () => {
    const consentsItem = {
      partner_id: 'dinum-ami',
      partner_name: 'AMI',
      consent_datetime: new Date('2026-02-21T15:50:00Z'),
    };
    const partnersItem = {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'https://fake-link-1',
    };
    const partners = new Partners([partnersItem]);
    const consents = new Consents({ consents: [consentsItem] }, partners.items);
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);
    vi.spyOn(consents, 'hasAnyConsents').mockResolvedValue(true);
  });
  test('user has to be connected', async () => {
    // Given
    const followup = new Followup();
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, {
      props: {
        data: {
          followup,
          isFollowupEmpty: true,
          hasAnyConsents: true,
          hasAllConsents: false,
          partners: new Partners(),
        },
        params: {},
      },
    });

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });
  test('Should display current followup', async () => {
    // Given
    const followup = new Followup();
    vi.spyOn(followup, 'items', 'get').mockReturnValue([
      new FollowupItem(
        'partner',
        'type',
        'id1',
        'ref1',
        'notifications',
        null,
        null,
        [],
        'Opération Tranquillité Vacances',
        'subheading',
        'Votre demande est en cours de traitement.',
        'icon',
        new Date('2026-02-22T15:55:00.000Z'),
        'wip',
        'En cours',
        false,
        null,
        []
      ),
    ]);
    vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
      new FollowupItem(
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
        'Votre demande est terminée.',
        'icon',
        new Date('2026-02-20T15:55:00.000Z'),
        'closed',
        'Terminée',
        true,
        null,
        []
      ),
    ]);
    const spy = vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

    // When
    render(Page, {
      props: {
        data: {
          followup,
          isFollowupEmpty: false,
          hasAnyConsents: true,
          hasAllConsents: false,
          partners: new Partners(),
        },
        params: {},
      },
    });

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('followup')).toHaveTextContent(
        'Votre demande est en cours de traitement.'
      );
      expect(screen.getByTestId('followup')).not.toHaveTextContent(
        'Votre demande est terminée.'
      );
    });
  });
});
