import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import type { APIConsents } from '$lib/api-consents';
import type { APIPartnersItem } from '$lib/api-partners';
import * as consentsMethods from '$lib/consents';
import { Consents } from '$lib/consents';
import * as partnersMethods from '$lib/partners';
import { Partners } from '$lib/partners';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const partners = new Partners();
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, { props: { data: { partners: partners }, params: {} } });

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });

  test('should enable consent when user toggles on', async () => {
    // Given
    await userStore.login(mockUserInfo);

    const apiConsents: APIConsents = { consents: [] };
    const consents: Consents = new Consents(apiConsents);
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);

    const spy = vi.spyOn(consentsMethods, 'updateConsent').mockResolvedValue();

    const apiPartnersItem: APIPartnersItem = {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'http://fake-link',
    };
    const partners = new Partners([apiPartnersItem]);
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);
    render(Page, { props: { data: { partners: partners }, params: {} } });

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

    const apiConsents: APIConsents = { consents: [] };
    const consents: Consents = new Consents(apiConsents);
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);

    const spy = vi.spyOn(consentsMethods, 'updateConsent').mockResolvedValue();

    const apiPartnersItem: APIPartnersItem = {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'http://fake-link',
    };
    const partners = new Partners([apiPartnersItem]);
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);
    render(Page, { props: { data: { partners: partners }, params: {} } });

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

  test('should import NavWithBackButton component', async () => {
    // Given
    const partners = new Partners();

    // When
    render(Page, { props: { data: { partners: partners }, params: {} } });
    const backButton = screen.getByTestId('back-button');

    // Then
    expect(backButton).toBeInTheDocument();
    expect(screen.getByText('Suivi des démarches')).toBeInTheDocument();
  });

  test('should render a Back button', async () => {
    // Given
    const partners = new Partners();

    // When
    render(Page, { props: { data: { partners: partners }, params: {} } });

    // Then
    expectBackButtonPresent(screen);
  });
});
