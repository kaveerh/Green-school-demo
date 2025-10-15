<template>
  <BaseModal
    v-model="isOpen"
    title="Delete User"
    size="small"
    variant="danger"
    confirmText="Delete User"
    cancelText="Cancel"
    :loading="isDeleting"
    @confirm="handleConfirm"
    @cancel="handleCancel"
  >
    <div class="delete-modal-content">
      <!-- Warning Icon -->
      <div class="warning-icon">⚠️</div>

      <!-- User Info -->
      <div v-if="user" class="user-info">
        <p class="user-name">{{ user.full_name }}</p>
        <p class="user-email">{{ user.email }}</p>
      </div>

      <!-- Warning Message -->
      <p class="warning-message">
        Are you sure you want to delete this user? This action cannot be undone.
      </p>

      <!-- Additional Info -->
      <div class="info-box">
        <p class="info-title">What happens when you delete a user:</p>
        <ul class="info-list">
          <li>User will be marked as deleted (soft delete)</li>
          <li>User will no longer be able to log in</li>
          <li>User data will be retained for audit purposes</li>
          <li>User will not appear in active user lists</li>
        </ul>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import type { User } from '@/types/user'

interface Props {
  modelValue: boolean
  user: User | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', userId: string): void
  (e: 'cancel'): void
}>()

const isOpen = ref(props.modelValue)
const isDeleting = ref(false)

/**
 * Watch for modelValue changes
 */
watch(() => props.modelValue, (newValue) => {
  isOpen.value = newValue
})

/**
 * Watch for isOpen changes
 */
watch(isOpen, (newValue) => {
  emit('update:modelValue', newValue)
})

/**
 * Handle confirm deletion
 */
function handleConfirm() {
  if (!props.user) return

  isDeleting.value = true
  emit('confirm', props.user.id)
}

/**
 * Handle cancel
 */
function handleCancel() {
  emit('cancel')
}

/**
 * Reset deleting state when modal closes
 */
watch(isOpen, (newValue) => {
  if (!newValue) {
    isDeleting.value = false
  }
})
</script>

<style scoped>
.delete-modal-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  text-align: center;
}

.warning-icon {
  font-size: 4rem;
  line-height: 1;
}

.user-info {
  width: 100%;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #dc3545;
}

.user-name {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.user-email {
  margin: 0;
  font-size: 0.9rem;
  color: #6c757d;
}

.warning-message {
  margin: 0;
  font-size: 1rem;
  color: #2c3e50;
  line-height: 1.5;
}

.info-box {
  width: 100%;
  padding: 1rem;
  background: #fff3cd;
  border-radius: 4px;
  text-align: left;
}

.info-title {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #856404;
}

.info-list {
  margin: 0;
  padding-left: 1.5rem;
  font-size: 0.85rem;
  color: #856404;
}

.info-list li {
  margin-bottom: 0.25rem;
}

.info-list li:last-child {
  margin-bottom: 0;
}
</style>
