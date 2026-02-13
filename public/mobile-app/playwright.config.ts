import { defineConfig } from '@playwright/test';

export default defineConfig({
  webServer: {
    command: 'npm run build && npm run preview',
    port: 4173,
  },
  use: {
    baseURL: 'https://localhost:4173',
    ignoreHTTPSErrors: true,
  },
  testDir: 'e2e',
});
