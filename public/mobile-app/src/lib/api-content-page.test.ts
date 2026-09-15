import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { retrieveContentPage } from '$lib/api-content-page';

const contentPageData = {
  slug: 'accessibilite',
  title: 'Accessibilité',
  sections: [
    { slug: 'declaration', title: 'Déclaration', text: '# title\n\ntext' },
    { slug: 'recours', title: 'Recours', text: '' },
  ],
};

describe('/api-content-page', () => {
  describe('retrieveContentPage', () => {
    test('should get page content from API', async () => {
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(contentPageData), { status: 200 })
        );

      // When
      const result = await retrieveContentPage('accessibilite');

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/page/accessibilite');
      expect(result).toEqual(contentPageData);
    });
  });
});
