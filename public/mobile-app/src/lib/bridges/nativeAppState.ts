export const isNative = (): boolean => {
  return !!window.NativeAppState;
};

export const isPushNotificationEnabled = (): boolean => {
  if (isNative()) {
    return window.NativeAppState?.isPushNotificationEnabled() || false;
  } else {
    return false;
  }
};
