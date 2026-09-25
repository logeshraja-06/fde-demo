import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// Vite configuration
// ------------------
// In Phase 7, we add reverse proxy routing to http://127.0.0.1:8000
// to guarantee 100% reliable connections without IPv6/IPv4 localhost mismatch issues.

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    host: true, // Listen on all network addresses (0.0.0.0)
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/chat': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/rag': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/analytics': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
