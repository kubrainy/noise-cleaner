import tailwindcss from '@tailwindcss/vite'
import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  app: {
    head: {
      title: 'Noise Cleaner',
    },
  },
  css: ['~/assets/css/main.css'],
  modules: ['@nuxt/ui'],
  routeRules: {
    '/api/filter': { proxy: 'http://127.0.0.1:8000/api/filter' },
  },
  vite: {
    plugins: [tailwindcss()],
    server: {
      fs: {
        strict: false,
      },
    },
  },
})
