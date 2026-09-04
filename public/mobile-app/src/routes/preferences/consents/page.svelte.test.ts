import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import type { APIConsents } from '$lib/api-consents';
import type { APIPartners, APIPartnersItem } from '$lib/api-partners';
import * as consentsMethods from '$lib/consents';
import { Consents } from '$lib/consents';
import { Partners } from '$lib/partners';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const partners = new Partners();
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

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

    const spy = vi.spyOn(consentsMethods, 'updateConsent');

    const apiPartnersItem: APIPartnersItem = {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'http://fake-link',
    };
    const apiPartners: APIPartners = {
      partners: [apiPartnersItem],
    };
    const partners = new Partners(apiPartners);
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

  // test('should disable consent when user toggles off', async () => {
  //   // Given
  //   await userStore.login(mockUserInfo);
  //
  //   const spy = vi.spyOn(consentsMethods, 'updateConsent');
  //
  //   const apiPartnersItem: APIPartnersItem = {
  //     slug: 'dinum-ami',
  //     name: 'AMI',
  //     link: 'http://fake-link',
  //   }
  //   const apiPartners: APIPartners = {
  //     partners: [apiPartnersItem],
  //   }
  //   const partners = new Partners(apiPartners);
  //   render(Page, { props: { data: { partners: partners }, params: {} } });
  //
  //   const toggleInput: HTMLInputElement = screen.getByTestId('dinum-ami');
  //   console.log('init', toggleInput.checked);
  //   await waitFor(async () => {
  //     await fireEvent.click(toggleInput); // set toggle to checked
  //   });
  //
  //   // When
  //   console.log('after check', toggleInput.checked);
  //   await waitFor(async () => {
  //     expect(toggleInput.checked).toBeTruthy();
  //     expect(spy).toHaveBeenNthCalledWith(1, 'dinum-ami', true);
  //     await fireEvent.click(toggleInput);
  //
  //     console.log('after uncheck, in waitfor', toggleInput.checked);
  //   });
  //
  //   // Then
  //   await waitFor(async () => {
  //     console.log('after uncheck, outside waitfor', toggleInput.checked);
  //     expect(spy).toHaveBeenNthCalledWith(2, 'dinum-ami', false);
  //   });
  // });

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
