import { sveltekit } from '@sveltejs/kit/vite';
import { svelteTesting } from '@testing-library/svelte/vite';
import mkcert from 'vite-plugin-mkcert';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [sveltekit(), mkcert()],
  server: {
    proxy: {
      '/agent-admin': { target: 'http://localhost:8000', xfwd: true },
      '/api': { target: 'http://localhost:8000', xfwd: true },
      '/check-auth': { target: 'http://localhost:8000', xfwd: true },
      '/dev-utils': { target: 'http://localhost:8000', xfwd: true },
      '/login-ami-fi': { target: 'http://localhost:8000', xfwd: true },
      '/login-callback': { target: 'http://localhost:8000', xfwd: true },
      '/login-france-connect': { target: 'http://localhost:8000', xfwd: true },
      '/relogin-france-connect': { target: 'http://localhost:8000', xfwd: true },
      '/logout': { target: 'http://localhost:8000', xfwd: true },
      '/ping': { target: 'http://localhost:8000', xfwd: true },
      '/schema': { target: 'http://localhost:8000', xfwd: true },
      '/sector_identifier_url ': { target: 'http://localhost:8000', xfwd: true },
      '/silent-login-ami-fi': { target: 'http://localhost:8000', xfwd: true },
      '/static': { target: 'http://localhost:8000', xfwd: true },
      '/.well-known': { target: 'http://localhost:8000', xfwd: true },
    },
  },
  test: {
    projects: [
      {
        extends: './vite.config.ts',
        plugins: [svelteTesting()],
        test: {
          name: 'client',
          environment: 'jsdom',
          clearMocks: true,
          include: ['src/**/*.svelte.{test,spec}.{js,ts}'],
          exclude: ['src/lib/server/**'],
          setupFiles: ['./vitest-setup-client.ts'],
        },
      },
      {
        extends: './vite.config.ts',
        test: {
          name: 'server',
          environment: 'jsdom',
          include: ['src/**/*.{test,spec}.{js,ts}'],
          exclude: ['src/**/*.svelte.{test,spec}.{js,ts}'],
        },
      },
    ],
  },
  css: {
    lightningcss: {
      errorRecovery: true,
    },
  },
});
