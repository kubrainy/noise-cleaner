<script setup lang="ts">
const props = defineProps<{
  accept?: string
  maxSizeMb?: number
  disabled?: boolean
  title?: string
}>()

const emit = defineEmits<{
  (e: 'selected', file: File): void
  (e: 'error', message: string): void
  (e: 'cleared'): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const fileName = ref('')
const errorMessage = ref('')

function validate(file: File) {
  const name = file.name.toLowerCase()
  const isWavByType = file.type === 'audio/wav' || file.type === 'audio/x-wav'
  const isWavByExt = name.endsWith('.wav')

  if (!(isWavByExt || isWavByType)) {
    return 'Lütfen sadece .wav dosyası yükleyin.'
  }

  if (props.maxSizeMb != null) {
    const maxSizeBytes = props.maxSizeMb * 1024 * 1024
    if (file.size > maxSizeBytes) {
      return `Dosya boyutu ${props.maxSizeMb} MB'den büyük olamaz.`
    }
  }
  return null
}

function handleFile(file: File) {
  errorMessage.value = ''
  const error = validate(file)
  if (error) {
    errorMessage.value = error
    emit('error', error)
    return
  }
  fileName.value = file.name
  emit('selected', file)
}

function onInputChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file)
    return
  handleFile(file)
  input.value = ''
}

function openPicker() {
  if (props.disabled)
    return
  fileInput.value?.click()
}

function onDrop(event: DragEvent) {
  if (props.disabled)
    return
  isDragging.value = false
  const file = event.dataTransfer?.files[0]
  if (file) {
    handleFile(file)
  }
}

function clear() {
  if (props.disabled)
    return
  fileName.value = ''
  errorMessage.value = ''
  emit('cleared')
}
</script>

<template>
  <div class="rounded-2xl border border-slate-200/70 bg-white p-5 shadow-sm transition hover:shadow-md">
    <div v-if="props.title" class="mb-4 flex items-center gap-2.5">
      <span
        class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
        :class="fileName ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-500'"
      >
        <Icon v-if="fileName" name="heroicons:check" class="h-3.5 w-3.5" />
        <span v-else>1</span>
      </span>
      <span class="font-medium text-slate-800">{{ props.title }}</span>
    </div>

    <div
      class="rounded-xl border-2 border-dashed p-8 text-center transition-all"
      :class="[
        props.disabled
          ? 'cursor-not-allowed border-slate-200 bg-slate-50 opacity-50'
          : 'cursor-pointer border-slate-200 hover:border-blue-300 hover:bg-slate-50',
        isDragging ? 'border-blue-400 bg-blue-50/50' : '',
      ]"
      @click="openPicker"
      @dragenter="!props.disabled && (isDragging = true)"
      @dragover.prevent="!props.disabled && (isDragging = true)"
      @dragleave.self="isDragging = false"
      @drop.prevent="onDrop"
    >
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        :accept="props.accept"
        :disabled="props.disabled"
        @change="onInputChange"
      >

      <div class="flex flex-col items-center justify-center gap-3">
        <div
          class="flex h-12 w-12 items-center justify-center rounded-full transition-colors"
          :class="isDragging ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-400'"
        >
          <Icon name="heroicons:arrow-up-tray" class="h-5 w-5" />
        </div>

        <div class="text-sm text-slate-600">
          <span class="font-medium text-slate-700">Sürükle bırak</span> ya da tıklayarak yükle
          <div class="mt-1 text-xs text-slate-400">
            {{ props.accept ?? '.wav' }}<span v-if="props.maxSizeMb"> • maks {{ props.maxSizeMb }}MB</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="errorMessage" class="mt-3 flex items-center gap-1.5 text-sm text-red-600">
      <Icon name="heroicons:exclamation-circle" class="h-4 w-4 shrink-0" />
      {{ errorMessage }}
    </div>

    <div v-else-if="fileName" class="mt-3 flex items-center justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
      <div class="flex min-w-0 items-center gap-2 text-sm text-slate-700">
        <Icon name="heroicons:musical-note" class="h-4 w-4 shrink-0 text-blue-500" />
        <span class="truncate font-medium">{{ fileName }}</span>
      </div>
      <button
        type="button"
        aria-label="Dosyayı kaldır"
        class="shrink-0 rounded-md p-1 text-slate-400 transition-colors hover:bg-slate-200/70 hover:text-slate-600"
        @click.stop="clear"
      >
        <Icon name="heroicons:x-mark" class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>
