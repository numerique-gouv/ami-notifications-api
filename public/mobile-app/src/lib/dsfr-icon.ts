import dsfrIconList from '@gouvfr/dsfr/.config/icon.json';

export const getDSFRIcon = (icon: string, defaultIcon: string): string => {
  const customIcons = [
    'infinity-line',
    'folder-check-line',
    'folder-open-line',
    'indeterminate-circle-line',
  ];
  const iconList = [...dsfrIconList.map((i) => i.name), ...customIcons];

  return iconList.includes(icon?.replace('fr-icon-', '')) ? icon : defaultIcon;
};
