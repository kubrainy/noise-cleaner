import tailwindcss from '@tailwindcss/vite'
import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/app/assets/css/main.css'],
  modules: ['@nuxt/ui'],
  vite: {
    plugins: [tailwindcss()],
  },
})
