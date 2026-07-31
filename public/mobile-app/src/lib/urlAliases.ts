import * as self from './urlAliases';

interface UrlAlias {
  pattern: string;
  alias: string;
}

const urlAliases: UrlAlias[] = [
  { pattern: '/#/welcome/notifications', alias: 'welcome:notifications:activation' },
  {
    pattern: '/#/notifications-welcome-page',
    alias: 'welcome:notifications:activation',
  },
  {
    pattern: '/#/preferences/notifications',
    alias: 'preferences:notifications:activation',
  },
];

export const getUrlAliases = (): UrlAlias[] => {
  return urlAliases;
};

function patternToRegex(pattern: string): RegExp {
  const escaped = pattern
    .split('/')
    .map((segment) =>
      segment.startsWith(':') ? '[^/]+' : segment.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    )
    .join('/');
  return new RegExp(`^${escaped}$`);
}

export const resolveUrl = (url: string): string | null => {
  const match = self
    .getUrlAliases()
    .find(({ pattern }) => patternToRegex(pattern).test(url));
  return match?.alias || null;
};
