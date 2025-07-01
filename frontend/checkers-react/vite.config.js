import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  
  server: {
    proxy: {
      '/board': 'http://localhost:5173',
      '/move': 'http://localhost:5173',
      '/reset': 'http://localhost:5173',
    },
  },
})


