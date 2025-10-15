<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-overlay" @click="handleOverlayClick">
        <div class="modal-container" :class="modalSizeClass" @click.stop>
          <!-- Header -->
          <div class="modal-header" v-if="!hideHeader">
            <h3 class="modal-title">
              <slot name="title">{{ title }}</slot>
            </h3>
            <button
              v-if="!hideClose"
              class="modal-close"
              @click="handleClose"
              :disabled="loading"
              aria-label="Close modal"
            >
              ×
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <slot></slot>
          </div>

          <!-- Footer -->
          <div class="modal-footer" v-if="!hideFooter || $slots.footer">
            <slot name="footer">
              <button
                class="btn-secondary"
                @click="handleCancel"
                :disabled="loading"
              >
                {{ cancelText }}
              </button>
              <button
                class="btn-primary"
                :class="confirmButtonClass"
                @click="handleConfirm"
                :disabled="loading || confirmDisabled"
              >
                <span v-if="loading" class="spinner-small"></span>
                <span v-else>{{ confirmText }}</span>
              </button>
            </slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  size?: 'small' | 'medium' | 'large'
  hideHeader?: boolean
  hideFooter?: boolean
  hideClose?: boolean
  closeOnOverlay?: boolean
  confirmText?: string
  cancelText?: string
  confirmDisabled?: boolean
  loading?: boolean
  variant?: 'default' | 'danger' | 'warning' | 'success'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  size: 'medium',
  hideHeader: false,
  hideFooter: false,
  hideClose: false,
  closeOnOverlay: true,
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  confirmDisabled: false,
  loading: false,
  variant: 'default'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'close'): void
}>()

/**
 * Modal size class
 */
const modalSizeClass = computed(() => {
  return `modal-${props.size}`
})

/**
 * Confirm button class based on variant
 */
const confirmButtonClass = computed(() => {
  switch (props.variant) {
    case 'danger':
      return 'btn-danger'
    case 'warning':
      return 'btn-warning'
    case 'success':
      return 'btn-success'
    default:
      return ''
  }
})

/**
 * Handle overlay click
 */
function handleOverlayClick() {
  if (props.closeOnOverlay && !props.loading) {
    handleClose()
  }
}

/**
 * Handle close button
 */
function handleClose() {
  emit('update:modelValue', false)
  emit('close')
}

/**
 * Handle confirm button
 */
function handleConfirm() {
  emit('confirm')
}

/**
 * Handle cancel button
 */
function handleCancel() {
  emit('update:modelValue', false)
  emit('cancel')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-small {
  max-width: 400px;
}

.modal-medium {
  max-width: 600px;
}

.modal-large {
  max-width: 900px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 2rem;
  line-height: 1;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
}

.modal-close:hover:not(:disabled) {
  background: #f8f9fa;
  color: #2c3e50;
}

.modal-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-body {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.btn-primary,
.btn-secondary,
.btn-danger,
.btn-warning,
.btn-success {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 100px;
}

.btn-primary {
  background: #42b883;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #35a372;
}

.btn-secondary {
  background: white;
  color: #42b883;
  border: 1px solid #42b883;
}

.btn-secondary:hover:not(:disabled) {
  background: #f8f9fa;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-warning:hover:not(:disabled) {
  background: #e0a800;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
}

.btn-primary:disabled,
.btn-secondary:disabled,
.btn-danger:disabled,
.btn-warning:disabled,
.btn-success:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-small {
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Modal transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}

@media (max-width: 768px) {
  .modal-container {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .btn-primary,
  .btn-secondary,
  .btn-danger,
  .btn-warning,
  .btn-success {
    width: 100%;
  }
}
</style>
