<script setup lang="ts">
import type { ChartConfiguration } from 'chart.js'
import {
  CategoryScale,
  Chart,
  Filler,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

const props = defineProps<{
  title: string
  labels: number[]
  data: number[]
  color: string
  xLabel: string
  yLabel: string
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

function buildConfig(devicePixelRatio?: number): ChartConfiguration<'line'> {
  return {
    type: 'line',
    data: {
      labels: props.labels.map(value => value.toFixed(2)),
      datasets: [{
        data: props.data,
        borderColor: props.color,
        backgroundColor: `${props.color}22`,
        borderWidth: 1.5,
        pointRadius: 0,
        fill: true,
      }],
    },
    options: {
      responsive: devicePixelRatio == null,
      maintainAspectRatio: false,
      animation: false,
      devicePixelRatio,
      scales: {
        x: {
          title: { display: true, text: props.xLabel, font: { size: 10 } },
          ticks: { maxTicksLimit: 5, font: { size: 9 } },
          grid: { display: false },
        },
        y: {
          title: { display: true, text: props.yLabel, font: { size: 10 } },
          ticks: { maxTicksLimit: 4, font: { size: 9 } },
          grid: { color: '#f1f5f9' },
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
  }
}

function render() {
  if (!canvasRef.value)
    return

  chart?.destroy()
  chart = new Chart(canvasRef.value, buildConfig())
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/ç/g, 'c')
    .replace(/ğ/g, 'g')
    .replace(/ı/g, 'i')
    .replace(/ö/g, 'o')
    .replace(/ş/g, 's')
    .replace(/ü/g, 'u')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function download() {
  if (!canvasRef.value)
    return

  const exportScale = 3
  const tempCanvas = document.createElement('canvas')
  tempCanvas.width = canvasRef.value.clientWidth
  tempCanvas.height = canvasRef.value.clientHeight

  const exportChart = new Chart(tempCanvas, buildConfig(exportScale))
  const url = exportChart.toBase64Image('image/png', 1)
  exportChart.destroy()

  const link = document.createElement('a')
  link.href = url
  link.download = `${slugify(props.title)}.png`
  link.click()
}

onMounted(render)
watch(() => [props.data, props.labels], render)
onBeforeUnmount(() => chart?.destroy())
</script>

<template>
  <div class="relative rounded-xl border border-slate-100 bg-slate-50/50 p-3 pb-10">
    <div class="mb-2 text-xs font-medium text-slate-600">
      {{ props.title }}
    </div>
    <div class="h-40">
      <canvas ref="canvasRef" />
    </div>
    <button
      type="button"
      title="Görseli indir"
      class="absolute bottom-2 left-2 flex h-6 w-6 items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-200/70 hover:text-slate-600"
      @click="download"
    >
      <Icon name="heroicons:arrow-down-tray" class="h-3.5 w-3.5" />
    </button>
  </div>
</template>
