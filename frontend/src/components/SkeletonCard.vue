<template>
  <div class="skeleton-card">
    <BaseSkeleton
      v-if="showAvatar"
      variant="avatar"
      :width="avatarSize"
      :height="avatarSize"
      class="skeleton-avatar"
    />
    <div class="skeleton-content">
      <BaseSkeleton variant="text" :width="titleWidth" height="1.5rem" />
      <BaseSkeleton
        v-for="i in lines"
        :key="i"
        variant="text"
        :width="i === lines ? '70%' : '100%'"
        class="skeleton-line"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseSkeleton from './BaseSkeleton.vue'

interface Props {
  showAvatar?: boolean
  avatarSize?: number
  lines?: number
  titleWidth?: string
}

withDefaults(defineProps<Props>(), {
  showAvatar: true,
  avatarSize: 50,
  lines: 3,
  titleWidth: '60%'
})
</script>

<style scoped>
.skeleton-card {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.skeleton-avatar {
  flex-shrink: 0;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skeleton-line {
  margin: 0;
}
</style>
