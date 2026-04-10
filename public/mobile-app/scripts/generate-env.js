import { readFileSync, writeFileSync } from 'fs';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const buildEnvPath = resolve(
  __dirname,
  '../.svelte-kit/output/prerendered/dependencies/_app/env.js'
);
const content = readFileSync(buildEnvPath, 'utf-8');

writeFileSync(resolve(__dirname, '../build/_app/env.js'), content);
console.log('env.js copié dans build/_app/env.js');
