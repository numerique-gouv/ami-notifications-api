/***

This helper sends an event to a javascript interface injected into the WebView from the mobile app native code.
If `window.NativeBridge` exists, it can be used to notify the native code.

***/

export const emit = (eventName: string, data?: any) => {
  const payload = {
    eventName: eventName,
    data: JSON.stringify(data || {}),
  }

  console.log('Trying to emit native event', eventName, data)

  if (isNative()) {
    // This is an interface that would have been injected in the WebView from the mobile app native code.
    window.NativeBridge.onEvent(eventName, payload.data)
    console.log('Emitted event', eventName, data)
  }
}

export const isNative = (): boolean => {
  return !!window.NativeBridge
}

export const runOrNativeEvent = (func: () => any, eventName: string, data?: any) => {
  if (isNative()) {
    console.log("We're in a native WebView, send an event")
    emit(eventName, data)
  } else {
    console.log("We're not in a native WebView, run a function")
    return func()
  }
}
