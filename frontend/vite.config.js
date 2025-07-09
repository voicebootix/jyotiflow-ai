import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    historyApiFallback: true, // Enable client-side routing in development
  },
  build: {
    rollupOptions: {
      // Ensure proper handling of routes in production
      external: [],
    },
  },
  // Handle client-side routing in preview mode
  preview: {
    historyApiFallback: true,
  },
})
