/***

This helper is sends an event to a javascript interface injected into the WebView from the mobile app native code.
If `window.NativeBridge` exists, it can be used to notify the native code.

***/

export const emit = (eventName: string, data: any) => {
  const payload = {
    eventName: eventName,
    data: JSON.stringify(data || {}),
  }

  console.log('Trying to emit native event', eventName, data)

  // @ts-expect-error: `NativeBridge` doesn't exist on the window object, unless it's injected.
  if (window.NativeBridge) {
    // This is an interface that would have been injected in the WebView from the mobile app native code.
    // @ts-expect-error: `NativeBridge` doesn't exist on the window object, unless it's injected.
    NativeBridge.onEvent(eventName, payload.data)
    console.log('Emitted event', eventName, data)
  }
}
