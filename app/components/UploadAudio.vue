<script setup lang="ts" >
    const props = defineProps<{
        accept?: string
        maxSizeMb?: number
        disabled?: boolean
        title?: string
    }>()

    const emit = defineEmits<{
       (e: 'selected', file: File): void,
       (e: 'error', message: string): void,
       (e: 'cleared'): void
    }>()

    const fileInput = ref<HTMLInputElement | null>(null)
    const isDragging = ref(false)
    const fileName = ref('')
    const errorMessage = ref('')

    const mode = ref<'upload' | 'record'>('upload')
    const isRecording = ref(false)
    const recordingSeconds = ref(0)
    let mediaRecorder: MediaRecorder | null = null
    let recordedChunks: Blob[] = []
    let mediaStream: MediaStream | null = null
    let timerInterval: ReturnType<typeof setInterval> | null = null

    const recordingTime = computed(() => {
        const m = Math.floor(recordingSeconds.value / 60).toString().padStart(2, '0')
        const s = (recordingSeconds.value % 60).toString().padStart(2, '0')
        return `${m}:${s}`
    })

    function setMode(next: 'upload' | 'record'){
        if(props.disabled || mode.value === next) return
        if(isRecording.value) stopRecording()
        mode.value = next
    }

    function validate(file: File) {
        const name = file.name.toLowerCase()
        const isWavByType = file.type === 'audio/wav' || file.type === 'audio/x-wav'
        const isWavByExt = name.endsWith('.wav')

        if(!(isWavByExt || isWavByType)){
            return 'Lütfen sadece .wav dosyası yükleyin.'
        }

        if(props.maxSizeMb != null){
            const maxSizeBytes = props.maxSizeMb * 1024 * 1024
            if(file.size > maxSizeBytes){
                return `Dosya boyutu ${props.maxSizeMb} MB'den büyük olamaz.`
            }
        }
        return null
    }

    function handleFile(file: File){
        errorMessage.value = ''
        const error = validate(file)
        if(error){
            errorMessage.value = error
            emit('error', error)
            return
        }
        fileName.value = file.name
        emit('selected', file)
    }

    function onInputChange(event: Event){
        const input = event.target as HTMLInputElement
        const file = input.files?.[0]
        if(!file) return
        handleFile(file)
        input.value = ''
    }

    function openPicker(){
        if(props.disabled) return
        fileInput.value?.click()
    }

    function onDrop(event: DragEvent){
        if(props.disabled) return
        isDragging.value = false
        const file = event.dataTransfer?.files[0]
        if(file){
            handleFile(file)
        }
    }

    function clear(){
        if(props.disabled) return
        fileName.value = ''
        errorMessage.value = ''
        emit('cleared')
    }

    async function startRecording(){
        if(props.disabled || isRecording.value) return
        errorMessage.value = ''
        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
        } catch {
            errorMessage.value = 'Mikrofona erişilemedi. Tarayıcı izinlerini kontrol edin.'
            emit('error', errorMessage.value)
            return
        }

        recordedChunks = []
        mediaRecorder = new MediaRecorder(mediaStream)
        mediaRecorder.ondataavailable = (event) => {
            if(event.data.size > 0) recordedChunks.push(event.data)
        }
        mediaRecorder.onstop = onRecordingStop
        mediaRecorder.start()

        isRecording.value = true
        recordingSeconds.value = 0
        timerInterval = setInterval(() => { recordingSeconds.value++ }, 1000)
    }

    function stopRecording(){
        if(!isRecording.value) return
        mediaRecorder?.stop()
        mediaStream?.getTracks().forEach(track => track.stop())
        mediaStream = null
        isRecording.value = false
        if(timerInterval){
            clearInterval(timerInterval)
            timerInterval = null
        }
    }

    async function onRecordingStop(){
        const blob = new Blob(recordedChunks, { type: mediaRecorder?.mimeType || 'audio/webm' })
        recordedChunks = []
        try {
            const wavFile = await convertBlobToWavFile(blob)
            handleFile(wavFile)
        } catch {
            errorMessage.value = 'Kayıt işlenirken bir hata oluştu.'
            emit('error', errorMessage.value)
        }
    }

    async function convertBlobToWavFile(blob: Blob): Promise<File> {
        const arrayBuffer = await blob.arrayBuffer()
        const AudioContextCtor = window.AudioContext || (window as any).webkitAudioContext
        const audioContext = new AudioContextCtor()
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
        const wavBuffer = encodeWav(audioBuffer)
        await audioContext.close()
        return new File([wavBuffer], `kayit-${Date.now()}.wav`, { type: 'audio/wav' })
    }

    function encodeWav(audioBuffer: AudioBuffer): ArrayBuffer {
        const numChannels = audioBuffer.numberOfChannels
        const sampleRate = audioBuffer.sampleRate
        const bitDepth = 16
        const bytesPerSample = bitDepth / 8

        const length = audioBuffer.length
        const interleaved = new Float32Array(length * numChannels)
        for(let channel = 0; channel < numChannels; channel++){
            const channelData = audioBuffer.getChannelData(channel)
            for(let i = 0; i < length; i++){
                interleaved[i * numChannels + channel] = channelData[i] ?? 0
            }
        }

        const dataSize = interleaved.length * bytesPerSample
        const buffer = new ArrayBuffer(44 + dataSize)
        const view = new DataView(buffer)

        writeString(view, 0, 'RIFF')
        view.setUint32(4, 36 + dataSize, true)
        writeString(view, 8, 'WAVE')
        writeString(view, 12, 'fmt ')
        view.setUint32(16, 16, true)
        view.setUint16(20, 1, true)
        view.setUint16(22, numChannels, true)
        view.setUint32(24, sampleRate, true)
        view.setUint32(28, sampleRate * numChannels * bytesPerSample, true)
        view.setUint16(32, numChannels * bytesPerSample, true)
        view.setUint16(34, bitDepth, true)
        writeString(view, 36, 'data')
        view.setUint32(40, dataSize, true)

        let offset = 44
        for(let i = 0; i < interleaved.length; i++, offset += 2){
            const sample = Math.max(-1, Math.min(1, interleaved[i] ?? 0))
            view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
        }

        return buffer
    }

    function writeString(view: DataView, offset: number, text: string){
        for(let i = 0; i < text.length; i++){
            view.setUint8(offset + i, text.charCodeAt(i))
        }
    }

    onBeforeUnmount(() => {
        if(timerInterval) clearInterval(timerInterval)
        mediaStream?.getTracks().forEach(track => track.stop())
    })

</script>

<template>
  <div class="bg-white rounded-md border border-slate-200 shadow-sm p-4 space-y-3">
    <div v-if="props.title" class="flex items-center gap-2 text-slate-700 font-semibold">
      <span class="text-slate-500">1.</span>
      <span>{{ props.title }}</span>
    </div>

    <div class="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1 text-sm">
      <button
        type="button"
        class="px-3 py-1 rounded transition"
        :class="mode === 'upload' ? 'bg-white shadow-sm text-slate-800 font-medium' : 'text-slate-500 hover:text-slate-700'"
        :disabled="props.disabled"
        @click="setMode('upload')"
      >
        Dosya Yükle
      </button>
      <button
        type="button"
        class="px-3 py-1 rounded transition"
        :class="mode === 'record' ? 'bg-white shadow-sm text-slate-800 font-medium' : 'text-slate-500 hover:text-slate-700'"
        :disabled="props.disabled"
        @click="setMode('record')"
      >
        Kaydet
      </button>
    </div>

    <div
      v-if="mode === 'upload'"
      @click="openPicker"
      class="min-h-[196px] flex items-center justify-center rounded-md border border-slate-200 bg-slate-50 p-8 text-center transition"
      :class="[
        props.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:bg-slate-100',
        isDragging ? 'ring-2 ring-blue-400 bg-blue-50/40' : '',
      ]"
      @dragenter="!props.disabled && (isDragging = true)"
      @dragover.prevent="!props.disabled && (isDragging = true)"
      @dragleave.self="isDragging = false"
      @drop.prevent="onDrop"
    >
      <input
        type="file"
        ref="fileInput"
        @change="onInputChange"
        class="hidden"
        :accept="props.accept"
        :disabled="props.disabled"
      />

      <div class="flex flex-col items-center justify-center gap-3">
        <div class="h-14 w-14 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-500">
          <UIcon name="i-heroicons-arrow-up-tray" class="h-6 w-6" />
        </div>

        <div class="text-center">
          <div class="text-slate-700 font-medium">
             Drag &amp; Drop or Click to Upload
          </div>

  <div class="mt-1 text-sm text-slate-500">
    ({{ props.accept ?? '.wav' }})
    <span v-if="props.maxSizeMb" class="text-slate-400">
      • max {{ props.maxSizeMb }}MB
    </span>
  </div>
</div>

      </div>
    </div>

    <div
      v-else
      class="min-h-[196px] flex items-center justify-center rounded-md border border-slate-200 bg-slate-50 p-8 text-center transition"
      :class="props.disabled ? 'opacity-50 cursor-not-allowed' : ''"
    >
      <div class="flex flex-col items-center justify-center gap-3">
        <div
          class="h-14 w-14 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-500"
          :class="isRecording ? 'ring-2 ring-red-400 text-red-500' : ''"
        >
          <UIcon name="i-heroicons-microphone" class="h-6 w-6" />
        </div>

        <div v-if="isRecording" class="text-red-600 font-medium tabular-nums">
          {{ recordingTime }}
        </div>
        <div v-else class="text-slate-700 font-medium">
          Mikrofonla kaydet
        </div>

        <UButton
          size="sm"
          :color="isRecording ? 'error' : 'primary'"
          variant="soft"
          :disabled="props.disabled"
          @click.stop="isRecording ? stopRecording() : startRecording()"
        >
          {{ isRecording ? 'Kaydı Durdur' : 'Kaydı Başlat' }}
        </UButton>
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