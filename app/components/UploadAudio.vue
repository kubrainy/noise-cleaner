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
  <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-3">
    <div v-if="props.title" class="flex items-center gap-2 text-slate-700 font-semibold">
      <span class="text-slate-500">1.</span>
      <span>{{ props.title }}</span>
    </div>

    <div
      class="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center transition"
      :class="[
        props.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:bg-slate-100',
        isDragging ? 'ring-2 ring-blue-400 bg-blue-50/40' : '',
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
        <div class="h-14 w-14 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-500">
          <Icon name="heroicons:arrow-up-tray" class="h-6 w-6" />
        </div>

        <div class="text-slate-700 font-medium">
          Drag &amp; Drop or Click to Upload
          <span class="text-slate-500 font-normal">({{ props.accept ?? '.wav' }})</span>
          <span v-if="props.maxSizeMb" class="text-slate-400 font-normal"> • max {{ props.maxSizeMb }}MB</span>
        </div>
      </div>
    </div>
    <div v-if="errorMessage" class="text-sm text-red-600">
      {{ errorMessage }}
    </div>
    <div v-else-if="fileName" class="text-sm text-slate-600">
      Selected: <span class="font-medium text-slate-800">{{ fileName }}</span>
    </div>
    <div class="flex justify-end">
      <UButton
        v-if="errorMessage || fileName"
        size="xs"
        variant="soft"
        color="primary"
        @click.stop="clear"
      >
        Temizle
      </UButton>
    </div>
  </div>
</template>
