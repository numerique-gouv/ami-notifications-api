import { sveltekit } from '@sveltejs/kit/vite';
import { svelteTesting } from '@testing-library/svelte/vite';
import mkcert from 'vite-plugin-mkcert';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [sveltekit(), mkcert()],
  server: {
    proxy: {
      '/agent-admin': { target: 'https://localhost:8000', xfwd: true, secure: false },
      '/api': { target: 'https://localhost:8000', xfwd: true, secure: false },
      '/check-auth': { target: 'https://localhost:8000', xfwd: true, secure: false },
      '/dev-utils': { target: 'https://localhost:8000', xfwd: true, secure: false },
      '/login-ami-fi': { target: 'https://localhost:8000', xfwd: true, secure: false },
      '/login-callback': {
        target: 'https://localhost:8000',
        xfwd: true,
        secure: false,
      },
      '/login-france-connect': {
        target: 'https://localhost:8000',
        xfwd: true,
        secure: false,
      },
      '/relogin-france-connect': {
        target: 'https://localhost:8000',
        xfwd: true,
        secure: false,
      },
      '/logout': { target: 'https://localhost:8000', xfwd: true, secure: false },
      '/ping': { target: 'https://localhost:8000', xfwd: true, secure: false },
      '/schema': { target: 'https://localhost:8000', xfwd: true, secure: false },
      '/sector_identifier_url ': {
        target: 'https://localhost:8000',
        xfwd: true,
        secure: false,
      },
      '/silent-login-ami-fi': {
        target: 'https://localhost:8000',
        xfwd: true,
        secure: false,
      },
      '/static': { target: 'https://localhost:8000', xfwd: true, secure: false },
      '/api/v2/users/notification/events/stream': {
        target: 'wss://localhost:8000',
        ws: true,
        secure: false,
      },
      '/.well-known': { target: 'https://localhost:8000', xfwd: true, secure: false },
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
          include: ['src/**/*.test.ts'],
          setupFiles: ['./vitest-setup-client.ts'],
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
