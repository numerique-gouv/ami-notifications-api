const isNative = (): boolean => {
  return !!window.NativeInfos;
};

const getNativeInfos = (): NativeInfosData | undefined => {
  if (isNative()) {
    return window.NativeInfos?.getInfos();
  } else {
    console.log("We're not in a native WebView");
  }
};

export const getDeviceId = () => {
  const infos = getNativeInfos();
  return infos?.device_id || '';
};

export const getVersion = () => {
  const infos = getNativeInfos();
  return infos?.version || '';
};
