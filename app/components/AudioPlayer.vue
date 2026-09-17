<script setup lang="ts">
const props = defineProps<{
  src: string
}>()

const audioRef = ref<HTMLAudioElement | null>(null)
const playing = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const muted = ref(false)

function togglePlay() {
  if (!audioRef.value)
    return

  if (playing.value)
    audioRef.value.pause()
  else
    audioRef.value.play()
}

function onTimeUpdate() {
  currentTime.value = audioRef.value?.currentTime ?? 0
}

function onLoadedMetadata() {
  duration.value = audioRef.value?.duration ?? 0
}

function onEnded() {
  playing.value = false
  currentTime.value = 0
}

function seek(event: Event) {
  const value = Number((event.target as HTMLInputElement).value)
  if (audioRef.value)
    audioRef.value.currentTime = value
  currentTime.value = value
}

function toggleMute() {
  if (!audioRef.value)
    return
  muted.value = !muted.value
  audioRef.value.muted = muted.value
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds))
    return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

watch(() => props.src, () => {
  playing.value = false
  currentTime.value = 0
  duration.value = 0
})
</script>

<template>
  <div class="flex w-full max-w-sm items-center gap-3 rounded-full bg-slate-900 px-4 py-2.5 text-white shadow-sm">
    <audio
      ref="audioRef"
      :src="props.src"
      class="hidden"
      @play="playing = true"
      @pause="playing = false"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @ended="onEnded"
    />

    <button
      type="button"
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/10 transition-colors hover:bg-white/20"
      @click="togglePlay"
    >
      <Icon :name="playing ? 'heroicons:pause-solid' : 'heroicons:play-solid'" class="h-4 w-4" />
    </button>

    <span class="shrink-0 text-xs tabular-nums text-white/80">
      {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
    </span>

    <input
      type="range"
      class="h-1 flex-1 cursor-pointer accent-white"
      min="0"
      :max="duration || 0"
      step="0.01"
      :value="currentTime"
      @input="seek"
    >

    <button
      type="button"
      class="flex h-6 w-6 shrink-0 items-center justify-center text-white/80 transition-colors hover:text-white"
      @click="toggleMute"
    >
      <Icon :name="muted ? 'heroicons:speaker-x-mark-solid' : 'heroicons:speaker-wave-solid'" class="h-4 w-4" />
    </button>
  </div>
</template>
