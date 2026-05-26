<template>
  <div class="kv">
    <span>{{ label }}</span>
    <code :class="{ long }">{{ value }}</code>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number, Boolean], required: true },
  long: { type: Boolean, default: false },
})
</script>
