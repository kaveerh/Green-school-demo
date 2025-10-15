<template>
  <div
    class="skeleton"
    :class="[
      `skeleton-${variant}`,
      { 'skeleton-animated': animated }
    ]"
    :style="skeletonStyle"
  >
    <!-- Circle variant has content for proper aspect ratio -->
    <span v-if="variant === 'circle'" class="skeleton-content"></span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'text' | 'rectangle' | 'circle' | 'avatar'
  width?: string | number
  height?: string | number
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'text',
  animated: true
})

/**
 * Compute skeleton styles
 */
const skeletonStyle = computed(() => {
  const style: Record<string, string> = {}

  // Width
  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  }

  // Height
  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }

  // Default heights for text variant
  if (props.variant === 'text' && !props.height) {
    style.height = '1rem'
  }

  // Default size for avatar/circle
  if ((props.variant === 'avatar' || props.variant === 'circle') && !props.width && !props.height) {
    style.width = '40px'
    style.height = '40px'
  }

  return style
})
</script>

<style scoped>
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 4px;
  display: inline-block;
}

.skeleton-animated {
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.skeleton-text {
  width: 100%;
  margin-bottom: 0.5rem;
}

.skeleton-rectangle {
  width: 100%;
  height: 100px;
}

.skeleton-circle,
.skeleton-avatar {
  border-radius: 50%;
}

.skeleton-content {
  display: block;
  padding-top: 100%; /* 1:1 aspect ratio */
}
</style>
