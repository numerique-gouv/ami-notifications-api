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
  interface Window {
    _paq?: (string | number | boolean | object)[][];
    NativeBridge?: {
      onEvent(eventName: string, data: unknown): void;
    };
  }
}

export {};
