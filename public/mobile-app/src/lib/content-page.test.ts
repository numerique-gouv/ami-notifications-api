import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiContentPageMethods from '$lib/api-content-page';
import { buildContentPage } from '$lib/content-page';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';

const contentPageData = {
  slug: 'accessibilite',
  title: 'Accessibilité',
  sections: [
    { slug: 'declaration', title: 'Déclaration', text: '# title\n\ntext' },
    { slug: 'recours', title: 'Recours', text: '' },
  ],
};

describe('/content-page.ts', () => {
  describe('buildContentPage', () => {
    test('should build content page from API result', async () => {
      const spy = vi
        .spyOn(apiContentPageMethods, 'retrieveContentPage')
        .mockResolvedValue(contentPageData);
      await userStore.login(mockUserInfo);

      // When
      await userStore.login(mockUserInfo);
      const contentPage = await buildContentPage('accessibilite');

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(contentPage.title).toEqual('Accessibilité');
      expect(contentPage.sections.length).toEqual(2);
      expect(contentPage.sections[0].title).toEqual('Déclaration');
      expect(contentPage.sections[0].text).toEqual('# title\n\ntext');
      expect(contentPage.sections[1].title).toEqual('Recours');
    });
  });
});
