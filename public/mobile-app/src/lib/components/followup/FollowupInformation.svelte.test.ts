import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as apiContentPageMethods from '$lib/api-content-page';
import FollowupInformation from './FollowupInformation.svelte';

describe('/FollowupInformation.svelte', () => {
  test('load component', async () => {
    // Given
    const contentPageData = {
      slug: 'custom-texts',
      title: 'Textes personnalisés',
      sections: [{ slug: 'followup', title: 'Followup', text: '* foo\n*bar' }],
    };
    const spy = vi
      .spyOn(apiContentPageMethods, 'retrieveContentPage')
      .mockResolvedValue(contentPageData);

    // When
    render(FollowupInformation);

    // Then
    await waitFor(async () => {
      expect(screen.queryByTestId('accordion-text')).toHaveTextContent('foo');
    });
    expect(spy).toHaveBeenCalledWith('custom-texts');
  });

  test('load component with default data', async () => {
    // Given
    const contentPageData = {
      slug: 'custom-texts',
      title: 'Textes personnalisés',
      sections: [{ slug: 'something-else', title: 'Followup', text: '* foo\n*bar' }],
    };
    const spy = vi
      .spyOn(apiContentPageMethods, 'retrieveContentPage')
      .mockResolvedValue(contentPageData);

    // When
    render(FollowupInformation);

    // Then
    await waitFor(async () => {
      // default text
      expect(screen.queryByTestId('accordion-text')).toHaveTextContent(
        'tranquillité vacances'
      );
    });
  });
});
