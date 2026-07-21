// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
  namespace App {
    // interface Error {}
    // interface Locals {}
    // interface PageData {}
    // interface PageState {}
    // interface Platform {}
  }
  interface DSFRModalInstance {
    disclose: () => void;
    conceal: () => void;
  }

  interface DSFRInstance {
    modal: DSFRModalInstance;
  }

  interface NativeInfosData {
    platform: 'android' | 'ios';
    app_name: string;
    version: string;
    build: number;
    environment: string;
    mode: string;
    device_id: string;
  }

  interface Window {
    _paq?: (string | number | boolean | object)[][];
    NativeBridge?: {
      onEvent(eventName: string, data: unknown): void;
    };
    NativeInfos?: {
      getInfos(): NativeInfosData;
    };
    dsfr: (element: Element | null) => DSFRInstance;
  }
}

export {};
