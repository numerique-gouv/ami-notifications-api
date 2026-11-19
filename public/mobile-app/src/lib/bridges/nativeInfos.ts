export const isNative = (): boolean => {
  return !!window.NativeInfos;
};

const getNativeInfos = (): NativeInfosData | undefined => {
  if (isNative()) {
    return window.NativeInfos?.getInfos();
  }
};

export const getDeviceId = () => {
  const infos = getNativeInfos();
  return infos?.device_id || '';
};

export const getPlatform = () => {
  const infos = getNativeInfos();
  return infos?.platform || '';
};

export const getVersion = () => {
  const infos = getNativeInfos();
  return infos?.version || '';
};

export const getPromotedUrlAliases = (): string[] => {
  const infos = getNativeInfos();
  return infos?.promoted_url_aliases || [];
};
