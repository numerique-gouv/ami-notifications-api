import DOMPurify from 'dompurify';
import { marked } from 'marked';

const ALLOWED_TAGS = ['p', 'strong', 'em', 'sup', 'sub'];
const ALLOWED_ATTR: string[] = [];

export function renderMarkdown(md: string): string {
  if (typeof window === 'undefined') {
    return marked.parse(md) as string;
  }
  const raw = marked.parse(md) as string;
  return DOMPurify.sanitize(raw, { ALLOWED_TAGS, ALLOWED_ATTR });
}

export function renderInlineMarkdown(md: string): string {
  if (typeof window === 'undefined') {
    return marked.parseInline(md) as string;
  }
  const raw = marked.parseInline(md) as string;
  return DOMPurify.sanitize(raw, { ALLOWED_TAGS, ALLOWED_ATTR });
}
