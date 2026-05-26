<template>
  <div class="pill" :class="ok ? 'ok' : 'bad'">
    <span>{{ ok ? '✓' : '×' }}</span>
    {{ label }}
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  ok: { type: Boolean, required: true },
})
</script>
