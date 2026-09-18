import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import type { APIPartnersItem } from '$lib/api-partners';
import * as consentsMethods from '$lib/consents';
import { Consents } from '$lib/consents';
import * as followupMethods from '$lib/followup';
import { Followup } from '$lib/followup';
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
    const displayWarningBlocks = new Map<string, boolean>();
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, {
      props: {
        data: {
          consentItems: [],
          partners: partners,
          followup: followup,
          displayWarningBlocks: displayWarningBlocks,
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

  test('should enable consent when user toggles on', async () => {
    // Given
    await userStore.login(mockUserInfo);

    const consentsItem = {
      partner_id: 'dinum-ami',
      consent_datetime: new Date('2026-02-21T15:50:00Z'),
    };
    const consents = new Consents({ consents: [consentsItem] }, ['dinum-ami']);
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);
    const spy = vi.spyOn(consentsMethods, 'updateConsent').mockResolvedValue();

    const apiPartnersItem: APIPartnersItem = {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'http://fake-link',
    };
    const partners = new Partners([apiPartnersItem]);
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);
    const followup = new Followup();
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
    const displayWarningBlocks = new Map<string, boolean>();

    render(Page, {
      props: {
        data: {
          consentItems: [],
          partners: partners,
          followup: followup,
          displayWarningBlocks: displayWarningBlocks,
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
      expect(spy).toHaveBeenCalledWith('dinum-ami', true);
    });
  });

  test('should disable consent when user toggles off', async () => {
    // Given
    await userStore.login(mockUserInfo);

    const spy = vi.spyOn(consentsMethods, 'updateConsent');

    const apiPartnersItem: APIPartnersItem = {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'http://fake-link',
    };
    const partners = new Partners([apiPartnersItem]);
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);
    const followup = new Followup();
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
    const displayWarningBlocks = new Map<string, boolean>();

    render(Page, {
      props: {
        data: {
          consentItems: [],
          partners: partners,
          followup: followup,
          displayWarningBlocks: displayWarningBlocks,
        },
        params: {},
      },
    });

    // When
    let toggleInput: HTMLInputElement = screen.getByTestId('dinum-ami');
    expect(toggleInput.checked).toBeFalsy();
    await fireEvent.click(toggleInput);

    toggleInput = screen.getByTestId('dinum-ami');
    expect(toggleInput.checked).toBeTruthy();
    await fireEvent.click(toggleInput);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('dinum-ami', false);
    });
  });

  test('should enable all consents when user clicks on "Tout suivre" button', async () => {
    // Given
    await userStore.login(mockUserInfo);

    const spy = vi.spyOn(consentsMethods, 'updateAllConsents');

    const consentsItem1 = {
      partner_id: 'dinum-ami',
      consent_datetime: null,
    };
    const consentsItem2 = {
      partner_id: 'dinum-dn',
      consent_datetime: null,
    };
    const consents = new Consents({ consents: [consentsItem1, consentsItem2] }, [
      'dinum-ami',
    ]);
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);

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
    const followup = new Followup();
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
    const displayWarningBlocks = new Map<string, boolean>();

    render(Page, {
      props: {
        data: {
          consentItems: [],
          partners: partners,
          followup: followup,
          displayWarningBlocks: displayWarningBlocks,
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
    const displayWarningBlocks = new Map<string, boolean>();

    // When
    render(Page, {
      props: {
        data: {
          consentItems: [],
          partners: partners,
          followup: followup,
          displayWarningBlocks: displayWarningBlocks,
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
    const displayWarningBlocks = new Map<string, boolean>();

    // When
    render(Page, {
      props: {
        data: {
          consentItems: [],
          partners: partners,
          followup: followup,
          displayWarningBlocks: displayWarningBlocks,
        },
        params: {},
      },
    });

    // Then
    expectBackButtonPresent(screen);
  });
});
