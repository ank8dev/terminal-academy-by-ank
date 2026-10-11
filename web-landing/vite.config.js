import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  base: './',
  plugins: [react()],
  resolve: {
    // Shared desktop code (~/App) must use this package's node_modules, not
    // terminal-academy-desktop/node_modules: otherwise a clean checkout fails to
    // resolve and a local one bundles a second copy of React.
    dedupe: ['react', 'react-dom', 'framer-motion', '@use-gesture/react', 'lucide-react', 'xterm', '@xterm/addon-fit'],
    alias: {
      '@': path.resolve(__dirname, './src'),
      '~': path.resolve(__dirname, '../terminal-academy-desktop/src'),
      '@tauri-apps/api/core': path.resolve(__dirname, './src/mockTauri.ts'),
      '@tauri-apps/api/event': path.resolve(__dirname, './src/mockTauri.ts')
    }
  },
  server: {
    fs: {
      allow: [
        path.resolve(__dirname, '.'),
        path.resolve(__dirname, '../terminal-academy-desktop')
      ]
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
        variant1: path.resolve(__dirname, 'variant-1.html'),
        variant2: path.resolve(__dirname, 'variant-2.html'),
        variant3: path.resolve(__dirname, 'variant-3.html'),
        variant4: path.resolve(__dirname, 'variant-4.html'),
        variant5: path.resolve(__dirname, 'variant-5.html'),
      }
    }
  }
});
