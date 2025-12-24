<script setup lang="ts" >
    defineProps({
        accept?: string,
        maxSizeMb?: number,
        disabled?: boolean,
        title?: string,
    })
    defineEmits({
        selected(file: File)
        error(message: string)
        cleared()
        )
    })
</script>


<template>
 <div>

 </div>
</template>