<template>
  <div class="subject-form-container">
    <!-- Header -->
    <div class="header">
      <h1 class="title">{{ isEditMode ? 'Edit Subject' : 'Create Subject' }}</h1>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="goBack">Cancel</button>
        <button class="btn btn-primary" :disabled="isSubmitting" @click="handleSubmit">
          {{ isSubmitting ? 'Saving...' : (isEditMode ? 'Update Subject' : 'Create Subject') }}
        </button>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="subject-form">
      <!-- Basic Information -->
      <div class="form-section">
        <h2 class="section-title">Basic Information</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="code" class="form-label">
              Subject Code <span class="required">*</span>
            </label>
            <input
              id="code"
              v-model="formData.code"
              type="text"
              class="form-input"
              placeholder="e.g., MATH, ELA, SCIENCE"
              :disabled="isEditMode"
              required
              @blur="formData.code = formatSubjectCode(formData.code)"
            />
            <small class="form-hint">
              Uppercase letters, numbers, and underscores only. Cannot be changed after creation.
            </small>
          </div>

          <div class="form-group">
            <label for="name" class="form-label">
              Subject Name <span class="required">*</span>
            </label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              class="form-input"
              placeholder="e.g., Mathematics"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="description" class="form-label">Description</label>
          <textarea
            id="description"
            v-model="formData.description"
            class="form-textarea"
            rows="3"
            placeholder="Brief description of the subject..."
          ></textarea>
        </div>
      </div>

      <!-- Classification -->
      <div class="form-section">
        <h2 class="section-title">Classification</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="category" class="form-label">
              Category <span class="required">*</span>
            </label>
            <select id="category" v-model="formData.category" class="form-select" required>
              <option value="core">Core</option>
              <option value="elective">Elective</option>
              <option value="enrichment">Enrichment</option>
              <option value="remedial">Remedial</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div class="form-group">
            <label for="subject_type" class="form-label">Subject Type</label>
            <select id="subject_type" v-model="formData.subject_type" class="form-select">
              <option value="">Select type...</option>
              <option value="academic">Academic</option>
              <option value="arts">Arts</option>
              <option value="physical">Physical Education</option>
              <option value="technical">Technical</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="formData.is_required" type="checkbox" />
              <div class="checkbox-info">
                <strong>Required Subject</strong>
                <small>Subject is mandatory for all students</small>
              </div>
            </label>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="formData.is_active" type="checkbox" />
              <div class="checkbox-info">
                <strong>Active</strong>
                <small>Subject is currently active and available</small>
              </div>
            </label>
          </div>
        </div>
      </div>

      <!-- Grade Levels -->
      <div class="form-section">
        <h2 class="section-title">
          Grade Levels <span class="required">*</span>
        </h2>
        <p class="section-description">Select at least one grade level (1-7)</p>

        <div class="grade-levels-grid">
          <label
            v-for="grade in [1, 2, 3, 4, 5, 6, 7]"
            :key="grade"
            class="grade-checkbox"
          >
            <input
              v-model="formData.grade_levels"
              type="checkbox"
              :value="grade"
            />
            <span class="grade-label">Grade {{ grade }}</span>
          </label>
        </div>

        <div v-if="formData.grade_levels.length === 0" class="validation-error">
          Please select at least one grade level
        </div>
      </div>

      <!-- Display Properties -->
      <div class="form-section">
        <h2 class="section-title">Display Properties</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="color" class="form-label">Color</label>
            <div class="color-picker-container">
              <input
                id="color"
                v-model="formData.color"
                type="color"
                class="color-input"
              />
              <input
                v-model="formData.color"
                type="text"
                class="form-input color-text-input"
                placeholder="#2196F3"
                pattern="^#[0-9A-Fa-f]{6}$"
                @blur="validateColor"
              />
              <button
                type="button"
                class="btn btn-secondary btn-sm"
                @click="useDefaultColor"
              >
                Use Default
              </button>
            </div>
            <small class="form-hint">Hex color format (#RRGGBB)</small>
          </div>

          <div class="form-group">
            <label for="icon" class="form-label">Icon</label>
            <div class="icon-input-container">
              <input
                id="icon"
                v-model="formData.icon"
                type="text"
                class="form-input"
                placeholder="🔢"
                maxlength="50"
              />
              <button
                type="button"
                class="btn btn-secondary btn-sm"
                @click="useDefaultIcon"
              >
                Use Default
              </button>
            </div>
            <small class="form-hint">Emoji or icon identifier</small>
          </div>
        </div>

        <div class="form-group">
          <label for="display_order" class="form-label">Display Order</label>
          <input
            id="display_order"
            v-model.number="formData.display_order"
            type="number"
            class="form-input"
            min="0"
            placeholder="0"
          />
          <small class="form-hint">Lower numbers appear first in sorted lists</small>
        </div>
      </div>

      <!-- Academic Properties -->
      <div class="form-section">
        <h2 class="section-title">Academic Properties</h2>

        <div class="form-group">
          <label for="credits" class="form-label">Credits</label>
          <input
            id="credits"
            v-model.number="formData.credits"
            type="number"
            class="form-input"
            min="0"
            step="0.5"
            placeholder="Optional"
          />
          <small class="form-hint">Credit hours for this subject (optional)</small>
        </div>
      </div>

      <!-- Subject Preview -->
      <div class="form-section">
        <h2 class="section-title">Preview</h2>
        <div class="subject-preview">
          <div
            class="preview-icon"
            :style="{ backgroundColor: formData.color || '#757575' }"
          >
            {{ formData.icon || '📝' }}
          </div>
          <div class="preview-info">
            <div class="preview-code">{{ formData.code || 'CODE' }}</div>
            <div class="preview-name">{{ formData.name || 'Subject Name' }}</div>
            <div class="preview-badges">
              <span
                class="badge"
                :style="{ backgroundColor: getCategoryColor(formData.category) }"
              >
                {{ getSubjectCategoryLabel(formData.category) }}
              </span>
              <span v-if="formData.is_required" class="badge badge-required">
                Required
              </span>
              <span v-if="formData.is_active" class="badge badge-active">
                Active
              </span>
            </div>
            <div v-if="formData.grade_levels.length > 0" class="preview-grades">
              {{ formatGradeLevels(formData.grade_levels) }}
            </div>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSubjectStore } from '@/stores/subjectStore'
import {
  getSubjectCategoryLabel,
  getCategoryColor,
  formatGradeLevels,
  getDefaultIcon,
  getDefaultColor,
  formatSubjectCode,
  isValidHexColor
} from '@/types/subject'
import type { SubjectCreateInput, SubjectUpdateInput, SubjectCategory, SubjectType } from '@/types/subject'

const router = useRouter()
const route = useRoute()
const subjectStore = useSubjectStore()

// State
const isEditMode = computed(() => !!route.params.id)
const subjectId = computed(() => route.params.id as string)
const isSubmitting = ref(false)
const error = ref<string | null>(null)

const formData = ref<{
  code: string
  name: string
  description: string
  category: SubjectCategory
  subject_type: SubjectType | ''
  grade_levels: number[]
  color: string
  icon: string
  display_order: number
  credits: number | null
  is_required: boolean
  is_active: boolean
}>({
  code: '',
  name: '',
  description: '',
  category: 'core',
  subject_type: '',
  grade_levels: [1, 2, 3, 4, 5, 6, 7],
  color: '#2196F3',
  icon: '',
  display_order: 0,
  credits: null,
  is_required: true,
  is_active: true
})

// Methods
async function loadSubject() {
  if (!isEditMode.value) return

  try {
    const subject = await subjectStore.fetchSubjectById(subjectId.value)

    formData.value = {
      code: subject.code,
      name: subject.name,
      description: subject.description || '',
      category: subject.category,
      subject_type: subject.subject_type || '',
      grade_levels: [...subject.grade_levels],
      color: subject.color || '#2196F3',
      icon: subject.icon || '',
      display_order: subject.display_order,
      credits: subject.credits,
      is_required: subject.is_required,
      is_active: subject.is_active
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load subject'
  }
}

async function handleSubmit() {
  error.value = null

  // Validation
  if (!formData.value.code || !formData.value.name) {
    error.value = 'Code and Name are required'
    return
  }

  if (formData.value.grade_levels.length === 0) {
    error.value = 'Please select at least one grade level'
    return
  }

  if (formData.value.color && !isValidHexColor(formData.value.color)) {
    error.value = 'Invalid color format. Use hex format like #2196F3'
    return
  }

  isSubmitting.value = true

  try {
    if (isEditMode.value) {
      await updateSubject()
    } else {
      await createSubject()
    }

    // Navigate back to list
    router.push('/subjects')
  } catch (err: any) {
    error.value = err.message || 'Failed to save subject'
  } finally {
    isSubmitting.value = false
  }
}

async function createSubject() {
  const schoolId = localStorage.getItem('current_school_id') || '60da2256-81fc-4ca5-bf6b-467b8d371c61'

  const subjectData: SubjectCreateInput = {
    school_id: schoolId,
    code: formData.value.code.toUpperCase(),
    name: formData.value.name,
    description: formData.value.description || undefined,
    category: formData.value.category,
    subject_type: formData.value.subject_type || undefined,
    grade_levels: formData.value.grade_levels,
    color: formData.value.color || undefined,
    icon: formData.value.icon || undefined,
    display_order: formData.value.display_order,
    credits: formData.value.credits || undefined,
    is_required: formData.value.is_required,
    is_active: formData.value.is_active
  }

  await subjectStore.createSubject(subjectData)
}

async function updateSubject() {
  const subjectData: SubjectUpdateInput = {
    name: formData.value.name,
    description: formData.value.description || undefined,
    category: formData.value.category,
    subject_type: formData.value.subject_type || undefined,
    grade_levels: formData.value.grade_levels,
    color: formData.value.color || undefined,
    icon: formData.value.icon || undefined,
    display_order: formData.value.display_order,
    credits: formData.value.credits || undefined,
    is_required: formData.value.is_required,
    is_active: formData.value.is_active
  }

  await subjectStore.updateSubject(subjectId.value, subjectData)
}

function useDefaultColor() {
  if (formData.value.code) {
    formData.value.color = getDefaultColor(formData.value.code)
  }
}

function useDefaultIcon() {
  if (formData.value.code) {
    formData.value.icon = getDefaultIcon(formData.value.code)
  }
}

function validateColor() {
  if (formData.value.color && !isValidHexColor(formData.value.color)) {
    formData.value.color = '#2196F3'
  }
}

function goBack() {
  router.push('/subjects')
}

// Lifecycle
onMounted(async () => {
  if (isEditMode.value) {
    await loadSubject()
  }
})
</script>

<style scoped>
.subject-form-container {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #c62828;
}

.subject-form {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section {
  padding: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.section-description {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.95rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.required {
  color: #f44336;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #42b883;
}

.form-textarea {
  resize: vertical;
}

.form-hint {
  display: block;
  color: #666;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: background 0.2s;
}

.checkbox-label:hover {
  background: #f8f9fa;
}

.checkbox-label input[type="checkbox"] {
  margin-top: 0.25rem;
  cursor: pointer;
}

.checkbox-info {
  flex: 1;
}

.checkbox-info strong {
  display: block;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.checkbox-info small {
  color: #666;
  font-size: 0.9rem;
}

.grade-levels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
}

.grade-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.grade-checkbox:hover {
  border-color: #42b883;
  background: #f0f9f4;
}

.grade-checkbox input[type="checkbox"]:checked + .grade-label {
  font-weight: 600;
  color: #42b883;
}

.grade-label {
  font-size: 1rem;
  color: #2c3e50;
}

.validation-error {
  color: #f44336;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.color-picker-container,
.icon-input-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.color-input {
  width: 60px;
  height: 44px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.color-text-input {
  flex: 1;
}

.subject-preview {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.preview-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.preview-info {
  flex: 1;
}

.preview-code {
  font-family: monospace;
  font-weight: 700;
  color: #2c3e50;
  font-size: 1.1rem;
}

.preview-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0.25rem 0;
}

.preview-badges {
  display: flex;
  gap: 0.5rem;
  margin: 0.5rem 0;
  flex-wrap: wrap;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  color: white;
}

.badge-required {
  background: #FF9800;
}

.badge-active {
  background: #4CAF50;
}

.preview-grades {
  color: #666;
  font-size: 0.95rem;
  margin-top: 0.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.btn-primary {
  background: #42b883;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #35a372;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}
</style>
