<template>
  <div class="base-select" :class="{ 'has-error': hasError, 'is-disabled': disabled }">
    <!-- Label -->
    <label v-if="label" :for="selectId" class="select-label">
      {{ label }}
      <span v-if="required" class="required-indicator">*</span>
    </label>

    <!-- Select Wrapper -->
    <div class="select-wrapper">
      <select
        :id="selectId"
        ref="selectRef"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        class="select-field"
        @change="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
      >
        <!-- Placeholder Option -->
        <option v-if="placeholder" value="" disabled :selected="!modelValue">
          {{ placeholder }}
        </option>

        <!-- Options from array -->
        <option
          v-for="option in normalizedOptions"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>

      <!-- Dropdown Icon -->
      <span class="select-icon">▼</span>
    </div>

    <!-- Help Text -->
    <p v-if="helpText && !hasError" class="help-text">
      {{ helpText }}
    </p>

    <!-- Error Message -->
    <p v-if="hasError" class="error-text">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

interface Props {
  modelValue?: string | number
  options: SelectOption[] | string[] | number[]
  label?: string
  placeholder?: string
  helpText?: string
  errorMessage?: string
  disabled?: boolean
  required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
  (e: 'change', value: string | number): void
  (e: 'blur', event: FocusEvent): void
  (e: 'focus', event: FocusEvent): void
}>()

const selectRef = ref<HTMLSelectElement | null>(null)

/**
 * Generate unique select ID
 */
const selectId = computed(() => {
  return `select-${Math.random().toString(36).substr(2, 9)}`
})

/**
 * Check if select has error
 */
const hasError = computed(() => {
  return !!props.errorMessage
})

/**
 * Normalize options to consistent format
 */
const normalizedOptions = computed((): SelectOption[] => {
  return props.options.map((option) => {
    // If option is already an object with label/value
    if (typeof option === 'object' && 'label' in option && 'value' in option) {
      return option as SelectOption
    }

    // If option is a primitive (string or number)
    return {
      label: String(option),
      value: option,
      disabled: false
    }
  })
})

/**
 * Handle change event
 */
function handleChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const value = target.value

  emit('update:modelValue', value)
  emit('change', value)
}

/**
 * Handle blur event
 */
function handleBlur(event: FocusEvent) {
  emit('blur', event)
}

/**
 * Handle focus event
 */
function handleFocus(event: FocusEvent) {
  emit('focus', event)
}

/**
 * Expose focus method
 */
defineExpose({
  focus: () => selectRef.value?.focus(),
  blur: () => selectRef.value?.blur()
})
</script>

<style scoped>
.base-select {
  margin-bottom: 1rem;
}

.select-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.9rem;
}

.required-indicator {
  color: #dc3545;
  margin-left: 0.25rem;
}

.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.select-field {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 0.75rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  color: #2c3e50;
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.select-field:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
}

.select-field:disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.base-select.has-error .select-field {
  border-color: #dc3545;
}

.base-select.has-error .select-field:focus {
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

.select-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #6c757d;
  font-size: 0.7rem;
}

.base-select.is-disabled .select-icon {
  color: #9e9e9e;
}

.help-text {
  margin: 0.5rem 0 0 0;
  font-size: 0.85rem;
  color: #6c757d;
}

.error-text {
  margin: 0.5rem 0 0 0;
  font-size: 0.85rem;
  color: #dc3545;
}

/* Placeholder styling */
.select-field option[disabled][selected] {
  color: #9e9e9e;
}
</style>
