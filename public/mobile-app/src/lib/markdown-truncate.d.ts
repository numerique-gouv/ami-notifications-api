declare module 'markdown-truncate';

declare function truncateMarkdown(
  text: string,
  options: { limit?: number; ellipsis?: boolean }
): string;
