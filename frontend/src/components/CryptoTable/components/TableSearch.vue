<template>
  <div class="search-box">
    <span class="search-icon">🔍</span>
    <input 
      type="text" 
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      placeholder="Search coin..." 
      class="search-input"
    >
  </div>
</template>

<script setup>
defineProps({
  modelValue: String
})

defineEmits(['update:modelValue'])
</script>
