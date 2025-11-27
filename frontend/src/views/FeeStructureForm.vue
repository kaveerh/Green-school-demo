<template>
  <div class="fee-structure-form">
    <div class="header">
      <h1 class="title">{{ isEditing ? 'Edit Fee Structure' : 'Create Fee Structure' }}</h1>
      <router-link to="/fee-structures" class="btn btn-secondary">Back to List</router-link>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error">{{ error }}</div>

    <form v-if="!loading" @submit.prevent="handleSubmit" class="form">
      <!-- Basic Information -->
      <div class="form-section">
        <h2 class="section-title">Basic Information</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="grade_level" class="label">Grade Level *</label>
            <select
              id="grade_level"
              v-model.number="form.grade_level"
              required
              class="input"
              :disabled="isEditing"
            >
              <option value="">Select grade</option>
              <option :value="1">Grade 1</option>
              <option :value="2">Grade 2</option>
              <option :value="3">Grade 3</option>
              <option :value="4">Grade 4</option>
              <option :value="5">Grade 5</option>
              <option :value="6">Grade 6</option>
              <option :value="7">Grade 7</option>
            </select>
            <div v-if="isEditing" class="field-hint">Grade level cannot be changed after creation</div>
          </div>

          <div class="form-group">
            <label for="academic_year" class="label">Academic Year *</label>
            <input
              id="academic_year"
              v-model="form.academic_year"
              type="text"
              required
              class="input"
              placeholder="2024-2025"
              pattern="\d{4}-\d{4}"
              :disabled="isEditing"
            />
            <div class="field-hint">Format: YYYY-YYYY (e.g., 2024-2025)</div>
          </div>
        </div>

        <div class="form-group">
          <label for="description" class="label">Description</label>
          <textarea
            id="description"
            v-model="form.description"
            rows="3"
            class="input"
            placeholder="Describe this fee structure..."
          />
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="form.is_active"
              class="checkbox"
            />
            <span>Active</span>
            <span class="checkbox-hint">Fee structure is currently in use</span>
          </label>
        </div>
      </div>

      <!-- Base Tuition Amounts -->
      <div class="form-section">
        <h2 class="section-title">Base Tuition Amounts</h2>
        <p class="section-description">
          Set the base tuition amounts for different payment frequencies. All three amounts are required.
        </p>

        <div class="form-row">
          <div class="form-group">
            <label for="yearly_amount" class="label">Yearly Tuition (R) *</label>
            <input
              id="yearly_amount"
              v-model.number="form.yearly_amount"
              type="number"
              step="0.01"
              min="0"
              required
              class="input"
              placeholder="0.00"
              @input="calculateOtherFrequencies"
            />
            <div class="field-hint">Base amount for yearly payment</div>
          </div>

          <div class="form-group">
            <label for="monthly_amount" class="label">Monthly Tuition (R) *</label>
            <input
              id="monthly_amount"
              v-model.number="form.monthly_amount"
              type="number"
              step="0.01"
              min="0"
              required
              class="input"
              placeholder="0.00"
            />
            <div v-if="suggestedMonthly" class="field-hint">
              Suggested: R {{ formatCurrency(suggestedMonthly) }}
              <button type="button" @click="form.monthly_amount = suggestedMonthly" class="btn-link-small">
                Use
              </button>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="weekly_amount" class="label">Weekly Tuition (R) *</label>
            <input
              id="weekly_amount"
              v-model.number="form.weekly_amount"
              type="number"
              step="0.01"
              min="0"
              required
              class="input"
              placeholder="0.00"
            />
            <div v-if="suggestedWeekly" class="field-hint">
              Suggested: R {{ formatCurrency(suggestedWeekly) }}
              <button type="button" @click="form.weekly_amount = suggestedWeekly" class="btn-link-small">
                Use
              </button>
            </div>
          </div>

          <div class="form-group">
            <!-- Empty space for symmetry -->
          </div>
        </div>
      </div>

      <!-- Payment Frequency Discounts -->
      <div class="form-section">
        <h2 class="section-title">Payment Frequency Discounts</h2>
        <p class="section-description">
          Optional discounts for different payment frequencies. These reduce the total amount when applied.
        </p>

        <div class="form-row">
          <div class="form-group">
            <label for="yearly_discount" class="label">Yearly Payment Discount (%)</label>
            <input
              id="yearly_discount"
              v-model.number="form.yearly_discount"
              type="number"
              step="0.1"
              min="0"
              max="100"
              class="input"
              placeholder="0.0"
            />
            <div class="field-hint">Discount for paying full year upfront</div>
          </div>

          <div class="form-group">
            <label for="monthly_discount" class="label">Monthly Payment Discount (%)</label>
            <input
              id="monthly_discount"
              v-model.number="form.monthly_discount"
              type="number"
              step="0.1"
              min="0"
              max="100"
              class="input"
              placeholder="0.0"
            />
            <div class="field-hint">Discount for monthly payments</div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="weekly_discount" class="label">Weekly Payment Discount (%)</label>
            <input
              id="weekly_discount"
              v-model.number="form.weekly_discount"
              type="number"
              step="0.1"
              min="0"
              max="100"
              class="input"
              placeholder="0.0"
            />
            <div class="field-hint">Discount for weekly payments</div>
          </div>

          <div class="form-group">
            <!-- Empty space for symmetry -->
          </div>
        </div>
      </div>

      <!-- Sibling Discounts -->
      <div class="form-section">
        <h2 class="section-title">Sibling Discounts</h2>
        <p class="section-description">
          Optional discounts for families with multiple children enrolled. Applied per child.
        </p>

        <div class="form-row">
          <div class="form-group">
            <label for="sibling_2_discount" class="label">2nd Child Discount (%)</label>
            <input
              id="sibling_2_discount"
              v-model.number="form.sibling_2_discount"
              type="number"
              step="0.1"
              min="0"
              max="100"
              class="input"
              placeholder="0.0"
            />
            <div class="field-hint">Discount for second child in family</div>
          </div>

          <div class="form-group">
            <label for="sibling_3_discount" class="label">3rd Child Discount (%)</label>
            <input
              id="sibling_3_discount"
              v-model.number="form.sibling_3_discount"
              type="number"
              step="0.1"
              min="0"
              max="100"
              class="input"
              placeholder="0.0"
            />
            <div class="field-hint">Discount for third child in family</div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="sibling_4_plus_discount" class="label">4th+ Child Discount (%)</label>
            <input
              id="sibling_4_plus_discount"
              v-model.number="form.sibling_4_plus_discount"
              type="number"
              step="0.1"
              min="0"
              max="100"
              class="input"
              placeholder="0.0"
            />
            <div class="field-hint">Discount for fourth child and beyond</div>
          </div>

          <div class="form-group">
            <!-- Empty space for symmetry -->
          </div>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="form.apply_sibling_to_all"
              class="checkbox"
            />
            <span>Apply sibling discounts to all children</span>
            <span class="checkbox-hint">If checked, discounts apply to all children including the first</span>
          </label>
        </div>
      </div>

      <!-- Preview Summary -->
      <div v-if="form.yearly_amount > 0" class="form-section preview-section">
        <h2 class="section-title">Preview Summary</h2>

        <div class="preview-card">
          <h3>{{ form.academic_year }} - Grade {{ form.grade_level || '?' }}</h3>

          <div class="preview-grid">
            <div class="preview-item">
              <span class="preview-label">Yearly Tuition:</span>
              <span class="preview-value">R {{ formatCurrency(form.yearly_amount) }}</span>
            </div>

            <div v-if="form.monthly_amount" class="preview-item">
              <span class="preview-label">Monthly Tuition:</span>
              <span class="preview-value">R {{ formatCurrency(form.monthly_amount) }}</span>
            </div>

            <div v-if="form.weekly_amount" class="preview-item">
              <span class="preview-label">Weekly Tuition:</span>
              <span class="preview-value">R {{ formatCurrency(form.weekly_amount) }}</span>
            </div>
          </div>

          <div v-if="hasDiscounts" class="preview-discounts">
            <h4>Active Discounts:</h4>
            <ul>
              <li v-if="form.yearly_discount > 0">
                Yearly Payment: {{ form.yearly_discount }}% off
              </li>
              <li v-if="form.monthly_discount > 0">
                Monthly Payment: {{ form.monthly_discount }}% off
              </li>
              <li v-if="form.weekly_discount > 0">
                Weekly Payment: {{ form.weekly_discount }}% off
              </li>
              <li v-if="form.sibling_2_discount > 0">
                2nd Child: {{ form.sibling_2_discount }}% off
              </li>
              <li v-if="form.sibling_3_discount > 0">
                3rd Child: {{ form.sibling_3_discount }}% off
              </li>
              <li v-if="form.sibling_4_plus_discount > 0">
                4th+ Child: {{ form.sibling_4_plus_discount }}% off
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" @click="handleCancel" class="btn btn-secondary">
          Cancel
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="submitting || !isFormValid"
        >
          {{ submitting ? 'Saving...' : (isEditing ? 'Update Fee Structure' : 'Create Fee Structure') }}
        </button>
      </div>
    </form>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      <p>{{ successMessage }}</p>
      <div class="success-actions">
        <router-link to="/fee-structures" class="btn btn-primary">View All Fee Structures</router-link>
        <button @click="resetForm" class="btn btn-secondary">Create Another</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFeeStructureStore } from '@/stores/feeStructureStore'
import { useSchool } from '@/composables/useSchool'
import type { FeeStructureCreateInput, FeeStructureUpdateInput } from '@/types/feeStructure'

const route = useRoute()
const router = useRouter()
const feeStructureStore = useFeeStructureStore()
const { currentSchoolId } = useSchool()

// State
const loading = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const isEditing = ref(false)

const form = ref({
  grade_level: null as number | null,
  academic_year: '',
  yearly_amount: 0,
  monthly_amount: 0,
  weekly_amount: 0,
  yearly_discount: 0,
  monthly_discount: 0,
  weekly_discount: 0,
  sibling_2_discount: 0,
  sibling_3_discount: 0,
  sibling_4_plus_discount: 0,
  apply_sibling_to_all: false,
  is_active: true
})

// Computed
const suggestedMonthly = computed(() => {
  if (!form.value.yearly_amount) return null
  return Math.round((form.value.yearly_amount / 12) * 100) / 100
})

const suggestedWeekly = computed(() => {
  if (!form.value.yearly_amount) return null
  return Math.round((form.value.yearly_amount / 52) * 100) / 100
})

const hasDiscounts = computed(() => {
  return (
    form.value.yearly_discount > 0 ||
    form.value.monthly_discount > 0 ||
    form.value.weekly_discount > 0 ||
    form.value.sibling_2_discount > 0 ||
    form.value.sibling_3_discount > 0 ||
    form.value.sibling_4_plus_discount > 0
  )
})

const isFormValid = computed(() => {
  return (
    form.value.grade_level !== null &&
    form.value.academic_year &&
    form.value.yearly_amount > 0 &&
    form.value.monthly_amount > 0 &&
    form.value.weekly_amount > 0
  )
})

// Methods
function calculateOtherFrequencies() {
  // Auto-suggest but don't auto-fill to allow manual override
  // The suggestions are shown via computed properties
}

async function loadFeeStructure(id: string) {
  loading.value = true
  error.value = null

  try {
    const feeStructure = await feeStructureStore.fetchFeeStructureById(id)

    form.value = {
      grade_level: feeStructure.grade_level,
      academic_year: feeStructure.academic_year,
      yearly_amount: feeStructure.yearly_amount,
      monthly_amount: feeStructure.monthly_amount || 0,
      weekly_amount: feeStructure.weekly_amount || 0,
      yearly_discount: feeStructure.yearly_discount || 0,
      monthly_discount: feeStructure.monthly_discount || 0,
      weekly_discount: feeStructure.weekly_discount || 0,
      sibling_2_discount: feeStructure.sibling_2_discount || 0,
      sibling_3_discount: feeStructure.sibling_3_discount || 0,
      sibling_4_plus_discount: feeStructure.sibling_4_plus_discount || 0,
      apply_sibling_to_all: feeStructure.apply_sibling_to_all || false,
      is_active: feeStructure.is_active
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load fee structure'
    console.error('Failed to load fee structure:', err)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!isFormValid.value || !currentSchoolId.value) return

  submitting.value = true
  error.value = null

  try {
    if (isEditing.value && route.params.id) {
      // Update existing fee structure
      const updateData: FeeStructureUpdateInput = {
        yearly_amount: form.value.yearly_amount,
        monthly_amount: form.value.monthly_amount,
        weekly_amount: form.value.weekly_amount,
        yearly_discount: form.value.yearly_discount || undefined,
        monthly_discount: form.value.monthly_discount || undefined,
        weekly_discount: form.value.weekly_discount || undefined,
        sibling_2_discount: form.value.sibling_2_discount || undefined,
        sibling_3_discount: form.value.sibling_3_discount || undefined,
        sibling_4_plus_discount: form.value.sibling_4_plus_discount || undefined,
        apply_sibling_to_all: form.value.apply_sibling_to_all,
        is_active: form.value.is_active
      }

      await feeStructureStore.updateFeeStructure(route.params.id as string, updateData)
      successMessage.value = 'Fee structure updated successfully!'
    } else {
      // Create new fee structure
      const createData: FeeStructureCreateInput = {
        school_id: currentSchoolId.value,
        grade_level: form.value.grade_level as number,
        academic_year: form.value.academic_year,
        yearly_amount: form.value.yearly_amount,
        monthly_amount: form.value.monthly_amount,
        weekly_amount: form.value.weekly_amount,
        is_active: form.value.is_active
      }

      // Add payment frequency discounts only if greater than 0
      if (form.value.yearly_discount > 0) {
        createData.yearly_discount = form.value.yearly_discount
      }
      if (form.value.monthly_discount > 0) {
        createData.monthly_discount = form.value.monthly_discount
      }
      if (form.value.weekly_discount > 0) {
        createData.weekly_discount = form.value.weekly_discount
      }

      // Add sibling discounts only if greater than 0
      if (form.value.sibling_2_discount > 0) {
        createData.sibling_2_discount = form.value.sibling_2_discount
      }
      if (form.value.sibling_3_discount > 0) {
        createData.sibling_3_discount = form.value.sibling_3_discount
      }
      if (form.value.sibling_4_plus_discount > 0) {
        createData.sibling_4_plus_discount = form.value.sibling_4_plus_discount
      }

      // Add apply_sibling_to_all setting
      if (form.value.apply_sibling_to_all) {
        createData.apply_sibling_to_all = form.value.apply_sibling_to_all
      }

      await feeStructureStore.createFeeStructure(createData)
      successMessage.value = `Fee structure for Grade ${form.value.grade_level} (${form.value.academic_year}) created successfully!`
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to save fee structure'
    console.error('Failed to save fee structure:', err)
  } finally {
    submitting.value = false
  }
}

function handleCancel() {
  router.push('/fee-structures')
}

function resetForm() {
  form.value = {
    grade_level: null,
    academic_year: '',
    yearly_amount: 0,
    monthly_amount: 0,
    weekly_amount: 0,
    yearly_discount: 0,
    monthly_discount: 0,
    weekly_discount: 0,
    sibling_2_discount: 0,
    sibling_3_discount: 0,
    sibling_4_plus_discount: 0,
    apply_sibling_to_all: false,
    is_active: true
  }
  successMessage.value = null
  isEditing.value = false
}

function formatCurrency(amount: number): string {
  return amount.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// Lifecycle
onMounted(() => {
  if (!currentSchoolId.value) {
    error.value = 'Please select a school first'
    return
  }

  // Check if editing
  if (route.params.id) {
    isEditing.value = true
    loadFeeStructure(route.params.id as string)
  }
})
</script>

<style scoped>
.fee-structure-form {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 1.875rem;
  font-weight: bold;
  color: #111827;
  margin: 0;
}

.loading {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.error {
  padding: 1rem;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.success-message {
  padding: 2rem;
  background: #d1fae5;
  border-radius: 8px;
  text-align: center;
}

.success-message p {
  font-size: 1.125rem;
  font-weight: 500;
  color: #065f46;
  margin-bottom: 1.5rem;
}

.success-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.form {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.form-section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.section-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 1.5rem 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9375rem;
  transition: all 0.2s;
}

.input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

.field-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.75rem;
  border-radius: 6px;
  transition: background 0.2s;
}

.checkbox-label:hover {
  background: #f9fafb;
}

.checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: auto;
}

.btn-link-small {
  background: none;
  border: none;
  color: #6366f1;
  font-size: 0.75rem;
  cursor: pointer;
  padding: 0;
  margin-left: 0.5rem;
  text-decoration: underline;
}

.btn-link-small:hover {
  color: #4f46e5;
}

.preview-section {
  background: #f9fafb;
}

.preview-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1.5rem;
}

.preview-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem 0;
}

.preview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 4px;
}

.preview-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.preview-value {
  color: #111827;
  font-weight: 600;
}

.preview-discounts {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.preview-discounts h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.5rem 0;
}

.preview-discounts ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.preview-discounts li {
  font-size: 0.875rem;
  color: #059669;
  padding: 0.25rem 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

/* Button Styles */
.btn {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn:hover {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #6366f1;
  color: white;
}

.btn-secondary {
  background: #64748b;
  color: white;
}

@media (max-width: 768px) {
  .fee-structure-form {
    padding: 1rem;
  }

  .form-row,
  .preview-grid {
    grid-template-columns: 1fr;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .success-actions {
    flex-direction: column;
  }
}
</style>
