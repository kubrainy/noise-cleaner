<template>
  <div class="min-h-screen bg-slate-50">
    <div class="mx-auto max-w-2xl px-6 pb-16 pt-6">
      <header class="mb-6 text-center">
        <div class="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
          <Icon name="heroicons:speaker-wave" class="h-6 w-6" />
        </div>
        <h1 class="text-2xl font-semibold tracking-tight text-slate-900">
          Noise Cleaner
        </h1>
        <p class="mt-2 text-sm text-slate-500">
          Ses dosyanı yükle, gürültü seviyesini ayarla ve temizle.
        </p>
      </header>
      <UMain as="main" class="space-y-4">
        <slot></slot>
      </UMain>
      <UFooter class="mt-10 border-t border-slate-200 pt-6">
        <template #left>
          <p class="text-xs text-slate-400">
            © {{ new Date().getFullYear() }} Noise Cleaner
          </p>
        </template>
      </UFooter>
    </div>
  </div>
</template>