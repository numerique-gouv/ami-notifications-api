const getHiddenBannerIds = (): string[] => {
  const storedHiddenBannerIds: string =
    localStorage.getItem('hidden_banner_ids') || '[]';
  return JSON.parse(storedHiddenBannerIds);
};

export const hideBanner = (id: string) => {
  const hiddenBannerIds = getHiddenBannerIds();
  hiddenBannerIds.push(id);
  localStorage.setItem('hidden_banner_ids', JSON.stringify(hiddenBannerIds));
};

export const isBannerHidden = (id: string): boolean => {
  const hiddenBannerIds = getHiddenBannerIds();
  return hiddenBannerIds.indexOf(id) >= 0;
};
