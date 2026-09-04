import DOMPurify from 'dompurify';
import truncateMarkdown from 'markdown-truncate';
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

export function willTruncateMarkdown(md: string, limit: number): boolean {
  const truncated = truncateMarkdown(md, { limit: limit, ellipsis: true });
  return truncated !== md;
}

export function renderTruncatedMarkdown(md: string, limit: number): string {
  const truncated = truncateMarkdown(md, { limit: limit, ellipsis: true });
  return renderMarkdown(truncated);
}
