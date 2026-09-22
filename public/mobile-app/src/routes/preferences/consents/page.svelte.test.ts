import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import type { APIPartnersItem } from '$lib/api-partners';
import * as consentsMethods from '$lib/consents';
import { Consents, ConsentsItem } from '$lib/consents';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem } from '$lib/followup';
import * as partnersMethods from '$lib/partners';
import { Partners } from '$lib/partners';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const partners = new Partners();
    const followup = new Followup();
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, {
      props: {
        data: {
          consentItems: [],
          partners: partners,
          followup: followup,
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

  describe('When user toggles on', () => {
    test('should enable consent', async () => {
      // Given
      await userStore.login(mockUserInfo);

      const partnersItem = {
        slug: 'dinum-ami',
        name: 'AMI',
        link: 'https://fake-link-1',
      };
      const partners = new Partners([partnersItem]);
      vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);

      const consentsItem = new ConsentsItem('dinum-ami', 'AMI', null);
      const consents = new Consents({ consents: [consentsItem] }, partners.items);
      vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);
      const spy = vi.spyOn(consentsItem, 'updateConsent').mockResolvedValue(true);

      const followup = new Followup();
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

      render(Page, {
        props: {
          data: {
            consentItems: [consentsItem],
            partners: partners,
            followup: followup,
          },
          params: {},
        },
      });

      // When
      const toggleInput: HTMLInputElement = screen.getByTestId('dinum-ami');
      expect(toggleInput.checked).toBeFalsy();
      await fireEvent.click(toggleInput);

      // Then
      await waitFor(async () => {
        expect(spy).toHaveBeenCalledWith(true);
      });
    });
  });

  describe('When user toggles off', () => {
    test('should disable consent', async () => {
      // Given
      await userStore.login(mockUserInfo);

      const apiPartnersItem: APIPartnersItem = {
        slug: 'dinum-ami',
        name: 'AMI',
        link: 'http://fake-link',
      };
      const partners = new Partners([apiPartnersItem]);
      vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);
      const followup = new Followup();
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

      const consentsItem = new ConsentsItem(
        'dinum-ami',
        'AMI',
        new Date('2026-02-21T15:50:00Z')
      );
      const consents = new Consents({ consents: [consentsItem] }, partners.items);
      vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);
      const spy = vi.spyOn(consentsItem, 'updateConsent').mockResolvedValue(true);

      render(Page, {
        props: {
          data: {
            consentItems: [consentsItem],
            partners: partners,
            followup: followup,
          },
          params: {},
        },
      });

      // When
      const toggleInput: HTMLInputElement = screen.getByTestId('dinum-ami');
      expect(toggleInput.checked).toBeTruthy();
      await fireEvent.click(toggleInput);

      // Then
      await waitFor(async () => {
        expect(spy).toHaveBeenCalledWith(false);
      });
    });

    test('should display warning block when there is at least one followup item for this partner', async () => {
      // Given
      await userStore.login(mockUserInfo);

      const apiPartnersItem: APIPartnersItem = {
        slug: 'dinum-ami',
        name: 'AMI',
        link: 'http://fake-link',
      };
      const partners = new Partners([apiPartnersItem]);
      vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);

      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'dinum-ami',
          'type',
          'id1',
          'ref1',
          'notifications',
          null,
          null,
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
        ),
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

      const consentsItem = new ConsentsItem(
        'dinum-ami',
        'AMI',
        new Date('2026-02-21T15:50:00Z')
      );
      const consents = new Consents({ consents: [consentsItem] }, partners.items);
      vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);
      const spy = vi.spyOn(consentsItem, 'updateConsent').mockResolvedValue(true);

      render(Page, {
        props: {
          data: {
            consentItems: [consentsItem],
            partners: partners,
            followup: followup,
          },
          params: {},
        },
      });

      // When
      const toggleInput: HTMLInputElement = screen.getByTestId('dinum-ami');
      expect(toggleInput.checked).toBeTruthy();
      await fireEvent.click(toggleInput);

      // Then
      await waitFor(async () => {
        expect(spy).toHaveBeenCalledWith(false);
        const warningBlock: HTMLElement = screen.getByTestId('warning-dinum-ami');
        expect(warningBlock).toBeInTheDocument();
      });
    });

    test('should not display warning block when there is no followup item for this partner', async () => {
      // Given
      await userStore.login(mockUserInfo);

      const apiPartnersItem: APIPartnersItem = {
        slug: 'dinum-ami',
        name: 'AMI',
        link: 'http://fake-link',
      };
      const partners = new Partners([apiPartnersItem]);
      vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);

      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'dinum-dn',
          'type',
          'id1',
          'ref1',
          'notifications',
          null,
          null,
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
        ),
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

      const consentsItem = new ConsentsItem(
        'dinum-ami',
        'AMI',
        new Date('2026-02-21T15:50:00Z')
      );
      const consents = new Consents({ consents: [consentsItem] }, partners.items);
      vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);
      const spy = vi.spyOn(consentsItem, 'updateConsent').mockResolvedValue(true);

      render(Page, {
        props: {
          data: {
            consentItems: [consentsItem],
            partners: partners,
            followup: followup,
          },
          params: {},
        },
      });

      // When
      const toggleInput: HTMLInputElement = screen.getByTestId('dinum-ami');
      expect(toggleInput.checked).toBeTruthy();
      await fireEvent.click(toggleInput);

      // Then
      await waitFor(async () => {
        expect(spy).toHaveBeenCalledWith(false);
        expect(screen.queryByTestId('warning-dinum-ami')).not.toBeInTheDocument();
      });
    });
  });

  test('should enable all consents when user clicks on "Tout suivre" button', async () => {
    // Given
    await userStore.login(mockUserInfo);

    const spy = vi.spyOn(consentsMethods, 'updateAllConsents').mockResolvedValue();

    const apiPartnersItem1: APIPartnersItem = {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'http://fake-link-1',
    };
    const apiPartnersItem2: APIPartnersItem = {
      slug: 'dinum-dn',
      name: 'Démarche Numérique',
      link: 'http://fake-link-2',
    };
    const partners = new Partners([apiPartnersItem1, apiPartnersItem2]);
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);

    const consentsItem1 = new ConsentsItem('dinum-ami', 'AMI', null);
    const consentsItem2 = new ConsentsItem('dinum-dn', 'Démarche Numérique', null);
    const consents = new Consents(
      { consents: [consentsItem1, consentsItem2] },
      partners.items
    );
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);

    const followup = new Followup();
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

    render(Page, {
      props: {
        data: {
          consentItems: [consentsItem1, consentsItem2],
          partners: partners,
          followup: followup,
        },
        params: {},
      },
    });

    // When
    let toggleInput1: HTMLInputElement = screen.getByTestId('dinum-ami');
    let toggleInput2: HTMLInputElement = screen.getByTestId('dinum-dn');
    expect(toggleInput1.checked).toBeFalsy();
    expect(toggleInput2.checked).toBeFalsy();

    const selectAllButton = screen.getByTestId('select-all-button');
    await fireEvent.click(selectAllButton);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith(true);
      toggleInput1 = screen.getByTestId('dinum-ami');
      toggleInput2 = screen.getByTestId('dinum-dn');
      expect(toggleInput1.checked).toBeTruthy();
      expect(toggleInput2.checked).toBeTruthy();
    });
  });

  test('should import NavWithBackButton component', async () => {
    // Given
    const partners = new Partners();
    const followup = new Followup();

    // When
    render(Page, {
      props: {
        data: {
          consentItems: [],
          partners: partners,
          followup: followup,
        },
        params: {},
      },
    });
    const backButton = screen.getByTestId('back-button');

    // Then
    expect(backButton).toBeInTheDocument();
    expect(screen.getByText('Suivi des démarches')).toBeInTheDocument();
  });

  test('should render a Back button', async () => {
    // Given
    const partners = new Partners();
    const followup = new Followup();

    // When
    render(Page, {
      props: {
        data: {
          consentItems: [],
          partners: partners,
          followup: followup,
        },
        params: {},
      },
    });

    // Then
    expectBackButtonPresent(screen);
  });
});
