import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { renderMarkdown } from './markdown';

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
  });
});
