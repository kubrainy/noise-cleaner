<script setup lang="ts">
import type { FilterConfig } from '~/components/FilterSelector.vue'
import type { FilterResult } from '~/components/FilterResults.vue'

useSeoMeta({
  title: 'Noise Cleaner – Ücretsiz Online Ses Gürültü Filtreleme Aracı',
  description: 'Ses dosyalarınızdaki istenmeyen gürültüyü ücretsiz ve online temizleyin. WAV dosyalarınıza yüksek geçiren, alçak geçiren ve bant geçiren filtreler uygulayın, sonucu anında dinleyip indirin.',
})

useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebApplication',
        'name': 'Noise Cleaner',
        'url': 'https://noise-cleaner-chi.vercel.app/',
        'description': 'Ses dosyalarındaki istenmeyen gürültüyü online temizleyen, yüksek geçiren, alçak geçiren ve bant geçiren filtreler sunan ücretsiz web uygulaması.',
        'applicationCategory': 'MultimediaApplication',
        'operatingSystem': 'Any',
        'offers': {
          '@type': 'Offer',
          'price': '0',
          'priceCurrency': 'USD',
        },
        'inLanguage': 'tr',
      }),
    },
  ],
})

const selectedFile = ref<File | null>(null)
const result = ref<FilterResult | null>(null)
const processing = ref(false)
const error = ref<string | null>(null)
const appliedFilterType = ref<FilterConfig['filterType'] | null>(null)

function onSelected(file: File) {
  selectedFile.value = file
  result.value = null
  error.value = null
}

function onCleared() {
  selectedFile.value = null
  result.value = null
  error.value = null
}

async function onProcess(config: FilterConfig) {
  if (!selectedFile.value)
    return

  processing.value = true
  error.value = null
  result.value = null
  appliedFilterType.value = config.filterType

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('filter_type', config.filterType)
  if (config.cutoff != null)
    formData.append('cutoff', String(config.cutoff))
  if (config.lowcut != null)
    formData.append('lowcut', String(config.lowcut))
  if (config.highcut != null)
    formData.append('highcut', String(config.highcut))

  try {
    result.value = await $fetch<FilterResult>('/api/filter', {
      method: 'POST',
      body: formData,
    })
  }
  catch {
    error.value = 'Ses işlenirken bir hata oluştu. Backend çalışıyor mu kontrol et.'
  }
  finally {
    processing.value = false
  }
}
</script>

<template>
  <UploadAudio
    title="Ses dosyası yükle"
    :max-size-mb="10"
    accept=".wav"
    @selected="onSelected"
    @cleared="onCleared"
  />
  <FilterSelector
    title="Filtre seç ve uygula"
    :disabled="!selectedFile"
    :loading="processing"
    @process="onProcess"
  />
  <FilterResults
    title="Sonuçlar"
    :result="result"
    :loading="processing"
    :error="error"
    :filter-type="appliedFilterType"
  />

  <UPageSection
    headline="Nasıl çalışır"
    title="Ses filtreleme türleri"
    description="Noise Cleaner, WAV dosyanıza uyguladığınız frekans filtresine göre istenmeyen gürültüyü ayıklar."
    :features="[
      {
        title: 'Yüksek Geçiren Filtre',
        description: 'Belirlediğiniz frekansın altındaki düşük tonlu gürültüyü (uğultu, rüzgar sesi gibi) süzer.',
        icon: 'i-heroicons-arrow-up-circle',
      },
      {
        title: 'Alçak Geçiren Filtre',
        description: 'Belirlediğiniz frekansın üstündeki tiz gürültüyü (hışırtı, cızırtı gibi) süzer.',
        icon: 'i-heroicons-arrow-down-circle',
      },
      {
        title: 'Bant Geçiren Filtre',
        description: 'Sadece belirlediğiniz frekans aralığını geçirir, aralık dışındaki tüm sesleri filtreler.',
        icon: 'i-heroicons-adjustments-horizontal',
      },
    ]"
    class="mt-8"
  />
</template>
