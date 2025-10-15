<template>
  <div class="base-input" :class="{ 'has-error': hasError, 'is-disabled': disabled }">
    <!-- Label -->
    <label v-if="label" :for="inputId" class="input-label">
      {{ label }}
      <span v-if="required" class="required-indicator">*</span>
    </label>

    <!-- Input Field -->
    <div class="input-wrapper">
      <!-- Prefix Icon/Text -->
      <span v-if="$slots.prefix || prefix" class="input-prefix">
        <slot name="prefix">{{ prefix }}</slot>
      </span>

      <!-- Input Element -->
      <input
        :id="inputId"
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :autocomplete="autocomplete"
        :maxlength="maxlength"
        :min="min"
        :max="max"
        :step="step"
        :pattern="pattern"
        class="input-field"
        :class="inputClass"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @keydown.enter="handleEnter"
      />

      <!-- Suffix Icon/Text -->
      <span v-if="$slots.suffix || suffix || showClearButton" class="input-suffix">
        <button
          v-if="showClearButton && modelValue && !disabled"
          type="button"
          class="clear-button"
          @click="handleClear"
          aria-label="Clear input"
        >
          ×
        </button>
        <slot name="suffix">{{ suffix }}</slot>
      </span>
    </div>

    <!-- Help Text -->
    <p v-if="helpText && !hasError" class="help-text">
      {{ helpText }}
    </p>

    <!-- Error Message -->
    <p v-if="hasError" class="error-text">
      {{ errorMessage }}
    </p>

    <!-- Character Count -->
    <p v-if="showCount && maxlength" class="char-count">
      {{ characterCount }}/{{ maxlength }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  modelValue?: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
  label?: string
  placeholder?: string
  helpText?: string
  errorMessage?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  autocomplete?: string
  maxlength?: number
  min?: number
  max?: number
  step?: number
  pattern?: string
  prefix?: string
  suffix?: string
  showClearButton?: boolean
  showCount?: boolean
  inputClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  required: false,
  showClearButton: false,
  showCount: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
  (e: 'blur', event: FocusEvent): void
  (e: 'focus', event: FocusEvent): void
  (e: 'enter', event: KeyboardEvent): void
  (e: 'clear'): void
}>()

const inputRef = ref<HTMLInputElement | null>(null)

/**
 * Generate unique input ID
 */
const inputId = computed(() => {
  return `input-${Math.random().toString(36).substr(2, 9)}`
})

/**
 * Check if input has error
 */
const hasError = computed(() => {
  return !!props.errorMessage
})

/**
 * Calculate character count
 */
const characterCount = computed(() => {
  return props.modelValue ? String(props.modelValue).length : 0
})

/**
 * Handle input event
 */
function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  let value: string | number = target.value

  // Convert to number for number inputs
  if (props.type === 'number' && value !== '') {
    value = parseFloat(value)
  }

  emit('update:modelValue', value)
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
 * Handle enter key
 */
function handleEnter(event: KeyboardEvent) {
  emit('enter', event)
}

/**
 * Handle clear button
 */
function handleClear() {
  emit('update:modelValue', '')
  emit('clear')
  inputRef.value?.focus()
}

/**
 * Expose focus method
 */
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur(),
  select: () => inputRef.value?.select()
})
</script>

<style scoped>
.base-input {
  margin-bottom: 1rem;
}

.input-label {
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

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper:focus-within {
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
}

.base-input.has-error .input-wrapper {
  border-color: #dc3545;
}

.base-input.has-error .input-wrapper:focus-within {
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

.base-input.is-disabled .input-wrapper {
  background: #f8f9fa;
  cursor: not-allowed;
}

.input-field {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: transparent;
  font-size: 1rem;
  color: #2c3e50;
  outline: none;
  font-family: inherit;
}

.input-field::placeholder {
  color: #9e9e9e;
}

.input-field:disabled {
  cursor: not-allowed;
  color: #6c757d;
}

.input-prefix,
.input-suffix {
  display: flex;
  align-items: center;
  padding: 0 0.75rem;
  color: #6c757d;
  font-size: 0.9rem;
}

.input-prefix {
  border-right: 1px solid #e0e0e0;
}

.input-suffix {
  border-left: 1px solid #e0e0e0;
}

.clear-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  padding: 0;
  background: #e0e0e0;
  border: none;
  border-radius: 50%;
  color: #6c757d;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.clear-button:hover {
  background: #d0d0d0;
  color: #2c3e50;
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

.char-count {
  margin: 0.5rem 0 0 0;
  font-size: 0.85rem;
  color: #6c757d;
  text-align: right;
}

/* Number input: hide spinner buttons */
input[type='number']::-webkit-inner-spin-button,
input[type='number']::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type='number'] {
  -moz-appearance: textfield;
}
</style>
