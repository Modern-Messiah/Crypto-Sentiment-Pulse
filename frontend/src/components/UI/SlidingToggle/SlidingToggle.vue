<template>
  <div :class="containerClass" ref="containerRef">
    <div class="sliding-indicator" :class="indicatorClass" :style="indicatorStyle"></div>
    <button 
      v-for="item in items" 
      :key="item.id"
      :class="[itemClass, { active: modelValue === item.id }]"
      @click="$emit('update:modelValue', item.id)"
      :title="item.title || ''"
    >
      <slot name="item" :item="item">
        {{ item.label }}
      </slot>
    </button>
  </div>
</template>

<script setup>
import { ref, toRef } from 'vue'
import { useSlidingIndicator } from '../../../composables/useSlidingIndicator'

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  items: {
    type: Array,
    required: true
  },
  containerClass: String,
  itemClass: String,
  indicatorClass: String
})

defineEmits(['update:modelValue'])

const containerRef = ref(null)
const { indicatorStyle } = useSlidingIndicator(
  containerRef, 
  toRef(() => props.modelValue)
)
</script>
