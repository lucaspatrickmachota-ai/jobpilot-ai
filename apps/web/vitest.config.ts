import { configDefaults, defineConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';

const rootDirectory = fileURLToPath(new URL('.', import.meta.url));

export default defineConfig({
  esbuild: {
    jsx: 'automatic',
  },
  resolve: {
    alias: {
      '@': rootDirectory,
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    exclude: [...configDefaults.exclude, 'e2e/**'],
  },
});
