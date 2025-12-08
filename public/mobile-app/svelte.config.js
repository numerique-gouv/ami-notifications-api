import adapter from '@sveltejs/adapter-static'
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://svelte.dev/docs/kit/integrations
  // for more information about preprocessors
  preprocess: vitePreprocess(),

  kit: {
    alias: {
      $routes: 'src/routes',
      $tests: 'tests',
    },
    router: {
      type: 'hash',
    },
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: undefined,
      precompress: false,
      strict: true,
    }),
    serviceWorker: {
      register: false,
    },
    env: {
      // Pick up the project's global .env file, based on the .env.template example file.
      dir: '../../',
    },
  },
}

export default config
