<script setup lang="ts">
export type FilterType = 'highpass' | 'lowpass' | 'bandpass'

export interface FilterConfig {
  filterType: FilterType
  cutoff?: number
  lowcut?: number
  highcut?: number
}

const props = defineProps<{
  title?: string
  disabled?: boolean
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'process', config: FilterConfig): void
}>()

const filterOptions: { value: FilterType, label: string, description: string }[] = [
  { value: 'highpass', label: 'Yüksek Geçiren', description: '3500 Hz altını süzer' },
  { value: 'lowpass', label: 'Alçak Geçiren', description: '2500 Hz üstünü süzer' },
  { value: 'bandpass', label: 'Bant Geçiren', description: '2000-3000 Hz aralığını geçirir' },
]

const filterRanges: Record<'highpass' | 'lowpass', { min: number, max: number, default: number }> & {
  bandpass: { min: number, max: number, lowDefault: number, highDefault: number }
} = {
  highpass: { min: 100, max: 4000, default: 3500 },
  lowpass: { min: 100, max: 3000, default: 2500 },
  bandpass: { min: 100, max: 4000, lowDefault: 2000, highDefault: 3000 },
}

const filterType = ref<FilterType>('highpass')
const cutoff = ref(filterRanges.highpass.default)
const lowcut = ref(filterRanges.bandpass.lowDefault)
const highcut = ref(filterRanges.bandpass.highDefault)

function selectFilter(value: FilterType) {
  if (props.disabled)
    return
  filterType.value = value
  if (value === 'bandpass') {
    lowcut.value = filterRanges.bandpass.lowDefault
    highcut.value = filterRanges.bandpass.highDefault
  }
  else {
    cutoff.value = filterRanges[value].default
  }
}

function submit() {
  if (props.disabled || props.loading)
    return

  if (filterType.value === 'bandpass') {
    emit('process', { filterType: filterType.value, lowcut: lowcut.value, highcut: highcut.value })
  }
  else {
    emit('process', { filterType: filterType.value, cutoff: cutoff.value })
  }
}
</script>

<template>
  <div
    class="rounded-2xl border border-slate-200/70 bg-white p-5 shadow-sm transition"
    :class="props.disabled ? 'opacity-50' : 'hover:shadow-md'"
  >
    <div v-if="props.title" class="mb-4 flex items-center gap-2.5">
      <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-500">
        2
      </span>
      <span class="font-medium text-slate-800">{{ props.title }}</span>
    </div>

    <div class="grid grid-cols-1 gap-2 sm:grid-cols-3">
      <button
        v-for="option in filterOptions"
        :key="option.value"
        type="button"
        :disabled="props.disabled"
        class="rounded-xl border p-3 text-left text-sm transition"
        :class="filterType === option.value
          ? 'border-blue-500 bg-blue-50/60 text-blue-700'
          : 'border-slate-200 text-slate-600 hover:border-slate-300'"
        @click="selectFilter(option.value)"
      >
        <div class="font-medium">{{ option.label }}</div>
        <div class="mt-0.5 text-xs text-slate-400">{{ option.description }}</div>
      </button>
    </div>

    <div class="mt-5 space-y-4">
      <template v-if="filterType === 'bandpass'">
        <div>
          <div class="mb-1.5 flex justify-between text-xs text-slate-500">
            <span>Alt kesim frekansı</span>
            <span class="font-medium text-slate-700">{{ lowcut }} Hz</span>
          </div>
          <USlider v-model="lowcut" :min="filterRanges.bandpass.min" :max="highcut - 100" :step="100" :disabled="props.disabled" />
        </div>
        <div>
          <div class="mb-1.5 flex justify-between text-xs text-slate-500">
            <span>Üst kesim frekansı</span>
            <span class="font-medium text-slate-700">{{ highcut }} Hz</span>
          </div>
          <USlider v-model="highcut" :min="lowcut + 100" :max="filterRanges.bandpass.max" :step="100" :disabled="props.disabled" />
        </div>
      </template>
      <template v-else>
        <div>
          <div class="mb-1.5 flex justify-between text-xs text-slate-500">
            <span>Kesim frekansı</span>
            <span class="font-medium text-slate-700">{{ cutoff }} Hz</span>
          </div>
          <USlider v-model="cutoff" :min="filterRanges[filterType].min" :max="filterRanges[filterType].max" :step="100" :disabled="props.disabled" />
        </div>
      </template>
    </div>

    <UButton
      block
      class="mt-5"
      :loading="props.loading"
      :disabled="props.disabled"
      @click="submit"
    >
      Gürültüyü Temizle
    </UButton>
  </div>
</template>
