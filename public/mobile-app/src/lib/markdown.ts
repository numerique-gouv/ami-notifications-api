import DOMPurify from 'dompurify';
import truncateMarkdown from 'markdown-truncate';
import { marked } from 'marked';

const ALLOWED_TAGS = ['p', 'strong', 'em', 'sup', 'sub'];
const ALLOWED_ATTR: string[] = [];
const ALLOWED_TAGS_ON_PAGE = [
  'h1',
  'h2',
  'h3',
  'h4',
  'h5',
  'p',
  'strong',
  'em',
  'sup',
  'sub',
  'ul',
  'li',
  'ol',
  'a',
];
const ALLOWED_ATTR_ON_PAGE = ['href', 'class'];

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

export function renderPageMarkdown(md: string): string {
  const renderer = new marked.Renderer();
  renderer.heading = ({ text, depth }) => {
    // increase title levels, so # → h2, ## → h3, etc.
    return `<h${depth + 1} class="fr-h${depth + 3}">${text}</h${depth}>`;
  };
  const options = { renderer };
  if (typeof window === 'undefined') {
    return marked.parse(md, options) as string;
  }
  const raw = marked.parse(md, options) as string;
  return DOMPurify.sanitize(raw, {
    ALLOWED_TAGS: ALLOWED_TAGS_ON_PAGE,
    ALLOWED_ATTR: ALLOWED_ATTR_ON_PAGE,
  });
}
