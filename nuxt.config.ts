import tailwindcss from '@tailwindcss/vite'
import { defineNuxtConfig } from 'nuxt/config'

const siteUrl = 'https://noise-cleaner-chi.vercel.app'
const siteName = 'Noise Cleaner'
const siteDescription = 'Noise Cleaner ile ses dosyalarınızdaki istenmeyen gürültüyü ücretsiz ve online temizleyin. WAV dosyalarınıza yüksek geçiren, alçak geçiren ve bant geçiren filtreler uygulayın, sonucu anında dinleyip indirin.'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  app: {
    head: {
      htmlAttrs: { lang: 'tr' },
      title: `${siteName} – Ücretsiz Online Ses Gürültü Filtreleme Aracı`,
      link: [
        { rel: 'canonical', href: siteUrl },
      ],
      meta: [
        { name: 'description', content: siteDescription },
        { name: 'robots', content: 'index, follow' },
        { name: 'author', content: siteName },
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: siteName },
        { property: 'og:title', content: `${siteName} – Ücretsiz Online Ses Gürültü Filtreleme Aracı` },
        { property: 'og:description', content: siteDescription },
        { property: 'og:url', content: siteUrl },
        { property: 'og:locale', content: 'tr_TR' },
        { name: 'twitter:card', content: 'summary' },
        { name: 'twitter:title', content: `${siteName} – Ücretsiz Online Ses Gürültü Filtreleme Aracı` },
        { name: 'twitter:description', content: siteDescription },
      ],
    },
  },
  css: ['~/assets/css/main.css'],
  modules: ['@nuxt/ui', '@vercel/analytics/nuxt'],
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
