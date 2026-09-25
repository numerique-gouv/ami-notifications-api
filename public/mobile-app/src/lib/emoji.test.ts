import DOMPurify from 'dompurify';
import { describe, expect, test } from 'vitest';
import { ariaHideDecorativeEmoji } from '$lib/emoji';

describe('/emoji.ts', () => {
  describe('ariaHideDecorativeEmoji', () => {
    test('digits, no emoji', () => {
      expect(ariaHideDecorativeEmoji('test - 42')).toEqual('test - 42');
    });
    test('multiple emojis', () => {
      expect(ariaHideDecorativeEmoji('tangerine 🍊 and lemon 🍋')).toEqual(
        'tangerine <span aria-hidden="true">🍊</span> and lemon <span aria-hidden="true">🍋</span>'
      );
    });
    test('emoji and markup', () => {
      expect(ariaHideDecorativeEmoji('<script>alert()</script> cherries 🍒')).toEqual(
        '&lt;script&gt;alert()&lt;/script&gt; cherries <span aria-hidden="true">🍒</span>'
      );
    });
    test('emoji and cleaned markup', () => {
      expect(
        ariaHideDecorativeEmoji(
          DOMPurify.sanitize('text with <script>alert()</script> <b>cherries 🍒</b>'),
          false
        )
      ).toEqual('text with  <b>cherries <span aria-hidden="true">🍒</span></b>');
    });
  });
});
