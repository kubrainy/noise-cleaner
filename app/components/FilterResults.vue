<script setup lang="ts">
import type { FilterType } from './FilterSelector.vue'

export interface FilterResult {
  sample_rate: number
  time_original: number[]
  original_signal: number[]
  time_filtered: number[]
  filtered_signal: number[]
  freq_original: number[]
  original_spectrum: number[]
  freq_filtered: number[]
  filtered_spectrum: number[]
  filtered_audio_base64: string
}

const props = defineProps<{
  title?: string
  result: FilterResult | null
  loading?: boolean
  error?: string | null
  filterType?: FilterType | null
}>()

const filterFileNames: Record<FilterType, string> = {
  highpass: 'yuksek-geciren',
  lowpass: 'alcak-geciren',
  bandpass: 'bant-geciren',
}

function download() {
  if (!props.result)
    return

  const suffix = props.filterType ? filterFileNames[props.filterType] : 'ses'

  const link = document.createElement('a')
  link.href = props.result.filtered_audio_base64
  link.download = `filtrelenmis-${suffix}.wav`
  link.click()
}
</script>

<template>
  <div class="rounded-2xl border border-slate-200/70 bg-white p-5 shadow-sm">
    <div v-if="props.title" class="mb-4 flex items-center gap-2.5">
      <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-500">
        3
      </span>
      <span class="font-medium text-slate-800">{{ props.title }}</span>
    </div>

    <div v-if="props.loading" class="flex flex-col items-center justify-center gap-3 py-10 text-sm text-slate-500">
      <Icon name="heroicons:arrow-path" class="h-6 w-6 animate-spin text-blue-500" />
      Ses işleniyor...
    </div>

    <div v-else-if="props.error" class="flex items-center gap-1.5 py-6 text-sm text-red-600">
      <Icon name="heroicons:exclamation-circle" class="h-4 w-4 shrink-0" />
      {{ props.error }}
    </div>

    <div v-else-if="!props.result" class="py-10 text-center text-sm text-slate-400">
      Sonuçları görmek için önce sesini yükle ve bir filtre uygula.
    </div>

    <template v-else>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <SignalChart
          title="Zaman Ekseni — Orijinal"
          :labels="props.result.time_original"
          :data="props.result.original_signal"
          color="#94a3b8"
          x-label="Zaman (s)"
          y-label="Genlik"
        />
        <SignalChart
          title="Zaman Ekseni — Filtrelenmiş"
          :labels="props.result.time_filtered"
          :data="props.result.filtered_signal"
          color="#2563eb"
          x-label="Zaman (s)"
          y-label="Genlik"
        />
        <SignalChart
          title="Frekans Uzayı — Orijinal"
          :labels="props.result.freq_original"
          :data="props.result.original_spectrum"
          color="#94a3b8"
          x-label="Frekans (Hz)"
          y-label="Genlik"
        />
        <SignalChart
          title="Frekans Uzayı — Filtrelenmiş"
          :labels="props.result.freq_filtered"
          :data="props.result.filtered_spectrum"
          color="#2563eb"
          x-label="Frekans (Hz)"
          y-label="Genlik"
        />
      </div>

      <div class="mt-5 flex flex-col items-center justify-center gap-3 rounded-xl bg-slate-50 p-4">
        <AudioPlayer :src="props.result.filtered_audio_base64" />
        <UButton
          variant="soft"
          icon="heroicons:arrow-down-tray"
          @click="download"
        >
          İndir
        </UButton>
      </div>
    </template>
  </div>
</template>
