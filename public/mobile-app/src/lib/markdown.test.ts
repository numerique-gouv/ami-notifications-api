import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { renderInlineMarkdown, renderMarkdown, renderPageMarkdown } from './markdown';

describe('/markdown.ts', () => {
  describe('renderMarkdown', () => {
    test('should render bold', () => {
      expect(renderMarkdown('**bold**')).toContain('<strong>bold</strong>');
    });

    test('should render italic', () => {
      expect(renderMarkdown('*italic*')).toContain('<em>italic</em>');
    });

    test('should render paragraph', () => {
      expect(renderMarkdown('hello')).toMatch(/^<p>hello<\/p>/);
    });

    test('should render sub and sup', () => {
      expect(
        renderMarkdown('Le 1<sup>er</sup> producteur de CO<sub>2</sub> au monde')
      ).toContain('Le 1<sup>er</sup> producteur de CO<sub>2</sub> au monde');
    });

    test('should strip unauthorized tags (ex: h1)', () => {
      const result = renderMarkdown('# Titre');
      expect(result).not.toMatch(/<h1/);
      expect(result).toContain('Titre');
    });

    test('should not render paragraphs when rendering inline', () => {
      expect(renderInlineMarkdown('*hello*\n\nworld')).toEqual(
        '<em>hello</em>\n\nworld'
      );
    });

    test('should render titles/listes/etc. when rendering pages', () => {
      expect(
        renderPageMarkdown('# hello\n\n* world\n* test\n<script>alert</script>')
      ).toEqual(
        '<h2 class="fr-h4">hello</h2><ul>\n<li>world</li>\n<li>test</li>\n</ul>\n'
      );
    });
  });
});
