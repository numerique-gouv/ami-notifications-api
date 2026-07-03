import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { renderMarkdown } from './markdown';

vi.mock('dompurify', () => ({
  default: {
    sanitize: (html: string) =>
      // strip unauthorized tags
      html.replace(/<\/?(?!(?:p|strong|em)(?:\s|>|\/))[\w]+[^>]*>/gi, ''),
  },
}));

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

    test('should strip unauthorized tags (ex: h1)', () => {
      const result = renderMarkdown('# Titre');
      expect(result).not.toMatch(/<h1/);
      expect(result).toContain('Titre');
    });
  });
});
