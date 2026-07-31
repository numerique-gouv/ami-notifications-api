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
