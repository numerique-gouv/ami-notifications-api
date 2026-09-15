import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as apiContentPageMethods from '$lib/api-content-page';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

const contentPageData = {
  slug: 'accessibilite',
  title: 'Accessibilité',
  sections: [
    { slug: 'declaration', title: 'Déclaration', text: '# title\n\ntext' },
    { slug: 'recours', title: 'Recours', text: '' },
  ],
};

describe('/+page.svelte', () => {
  test('load page', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const spy = vi
      .spyOn(apiContentPageMethods, 'retrieveContentPage')
      .mockResolvedValue(contentPageData);

    // When
    render(Page, { props: { params: { page_slug: 'accessibilite' } } });

    // Then
    await waitFor(() => {
      expect(screen.getByText('Accessibilité')).toBeInTheDocument();
      expect(document.querySelectorAll('li').length).toEqual(2);
    });
  });
});
