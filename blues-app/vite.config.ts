import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // GitHub Pages serves the app under /music/; the Netlify copy builds with BASE=/.
  base: process.env.BASE ?? '/music/',
})
