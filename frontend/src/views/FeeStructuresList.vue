<template>
  <div class="fee-structures-list">
    <div class="page-header">
      <h1>Fee Structures (Tuition Pricing)</h1>
      <router-link to="/fee-structures/create" class="btn btn-primary">
        Create Fee Structure
      </router-link>
    </div>

    <!-- Statistics Cards -->
    <div v-if="statistics" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total Fee Structures</div>
        <div class="stat-value">{{ statistics.total_fee_structures }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Active</div>
        <div class="stat-value">{{ statistics.active_fee_structures }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Academic Years</div>
        <div class="stat-value">{{ statistics.academic_years?.length || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Grades Covered</div>
        <div class="stat-value">{{ statistics.grades_covered?.length || 0 }}/7</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>Academic Year</label>
        <select v-model="filters.academic_year">
          <option value="">All Years</option>
          <option v-for="year in academicYears" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Grade Level</label>
        <select v-model="filters.grade_level">
          <option value="">All Grades</option>
          <option value="1">Grade 1</option>
          <option value="2">Grade 2</option>
          <option value="3">Grade 3</option>
          <option value="4">Grade 4</option>
          <option value="5">Grade 5</option>
          <option value="6">Grade 6</option>
          <option value="7">Grade 7</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Status</label>
        <select v-model="filters.is_active">
          <option value="">All</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <div class="filter-actions">
        <button @click="applyFilters" class="btn btn-secondary">
          Apply Filters
        </button>
        <button @click="clearFilters" class="btn btn-link">Clear</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">Loading fee structures...</div>

    <!-- Error State -->
    <div v-if="error" class="error-message">{{ error }}</div>

    <!-- Fee Structures Table -->
    <div v-if="!loading && feeStructures.length > 0" class="fee-structures-table-container">
      <table class="fee-structures-table">
        <thead>
          <tr>
            <th>Grade Level</th>
            <th>Academic Year</th>
            <th>Base Tuition (Yearly)</th>
            <th>Payment Frequencies</th>
            <th>Discounts</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="feeStructure in feeStructures" :key="feeStructure.id" :class="getRowClass(feeStructure)">
            <td>
              <span class="grade-badge">Grade {{ feeStructure.grade_level }}</span>
            </td>
            <td>
              <span class="academic-year">{{ feeStructure.academic_year }}</span>
            </td>
            <td>
              <div class="tuition-amount">
                R {{ formatCurrency(feeStructure.yearly_amount) }}
              </div>
            </td>
            <td>
              <div class="frequency-list">
                <div v-if="feeStructure.monthly_amount" class="frequency-item">
                  <span class="freq-label">Monthly:</span>
                  <span class="freq-value">R {{ formatCurrency(feeStructure.monthly_amount) }}</span>
                  <span v-if="feeStructure.monthly_discount > 0" class="discount-hint">
                    ({{ feeStructure.monthly_discount }}% off)
                  </span>
                </div>
                <div v-if="feeStructure.weekly_amount" class="frequency-item">
                  <span class="freq-label">Weekly:</span>
                  <span class="freq-value">R {{ formatCurrency(feeStructure.weekly_amount) }}</span>
                  <span v-if="feeStructure.weekly_discount > 0" class="discount-hint">
                    ({{ feeStructure.weekly_discount }}% off)
                  </span>
                </div>
              </div>
            </td>
            <td>
              <div class="discount-info">
                <div v-if="hasSiblingDiscounts(feeStructure)" class="discount-item">
                  Sibling Discounts
                </div>
                <div v-if="hasPaymentDiscounts(feeStructure)" class="discount-item">
                  Payment Discounts
                </div>
                <div v-if="!hasSiblingDiscounts(feeStructure) && !hasPaymentDiscounts(feeStructure)" class="text-muted">
                  None
                </div>
              </div>
            </td>
            <td>
              <span class="status-badge" :class="feeStructure.is_active ? 'status-active' : 'status-inactive'">
                {{ feeStructure.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <router-link
                  :to="`/fee-structures/${feeStructure.id}/edit`"
                  class="btn btn-sm btn-secondary"
                >
                  Edit
                </router-link>
                <router-link
                  :to="`/fee-structures/${feeStructure.id}`"
                  class="btn btn-sm btn-link"
                >
                  View
                </router-link>
                <button
                  @click="handleDelete(feeStructure)"
                  class="btn btn-sm btn-danger"
                >
                  Delete
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && feeStructures.length === 0" class="empty-state">
      <p>No fee structures found.</p>
      <router-link to="/fee-structures/create" class="btn btn-primary">
        Create First Fee Structure
      </router-link>
    </div>

    <!-- Pagination -->
    <div v-if="pages > 1" class="pagination">
      <button
        @click="goToPage(page - 1)"
        :disabled="page === 1"
        class="btn btn-secondary"
      >
        Previous
      </button>
      <span class="page-info">
        Page {{ page }} of {{ pages }} ({{ total }} total)
      </span>
      <button
        @click="goToPage(page + 1)"
        :disabled="page === pages"
        class="btn btn-secondary"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useFeeStructureStore } from '@/stores/feeStructureStore'
import { useSchool } from '@/composables/useSchool'
import { useRouter } from 'vue-router'
import type { FeeStructure } from '@/types/feeStructure'

const feeStructureStore = useFeeStructureStore()
const router = useRouter()
const { currentSchoolId } = useSchool()

// State
const filters = ref({
  academic_year: '',
  grade_level: '',
  is_active: ''
})

// Computed
const feeStructures = computed(() => feeStructureStore.feeStructures)
const loading = computed(() => feeStructureStore.loading)
const error = computed(() => feeStructureStore.error)
const statistics = computed(() => feeStructureStore.statistics)
const total = computed(() => feeStructureStore.pagination.total)
const page = computed(() => feeStructureStore.pagination.page)
const pages = computed(() => feeStructureStore.pagination.pages)

const academicYears = computed(() => {
  if (!statistics.value?.academic_years) return []
  return statistics.value.academic_years.sort().reverse()
})

// Methods
async function loadFeeStructures() {
  if (!currentSchoolId.value) {
    console.warn('Cannot load fee structures: no school selected')
    return
  }

  const params: any = {
    school_id: currentSchoolId.value,
    page: page.value,
    limit: 50
  }

  if (filters.value.academic_year) params.academic_year = filters.value.academic_year
  if (filters.value.grade_level) params.grade_level = parseInt(filters.value.grade_level)
  if (filters.value.is_active !== '') params.is_active = filters.value.is_active === 'true'

  try {
    await feeStructureStore.fetchFeeStructures(params)
  } catch (err) {
    console.error('Failed to load fee structures:', err)
  }
}

async function loadStatistics() {
  if (!currentSchoolId.value) {
    console.warn('Cannot load statistics: no school selected')
    return
  }

  try {
    await feeStructureStore.fetchStatistics(
      currentSchoolId.value,
      filters.value.academic_year || undefined
    )
  } catch (err) {
    console.error('Failed to load statistics:', err)
  }
}

function applyFilters() {
  feeStructureStore.pagination.page = 1
  loadFeeStructures()
  loadStatistics()
}

function clearFilters() {
  filters.value = {
    academic_year: '',
    grade_level: '',
    is_active: ''
  }
  applyFilters()
}

function goToPage(newPage: number) {
  feeStructureStore.pagination.page = newPage
  loadFeeStructures()
}

async function handleDelete(feeStructure: FeeStructure) {
  if (!confirm(`Are you sure you want to delete the fee structure for Grade ${feeStructure.grade_level} (${feeStructure.academic_year})?`)) {
    return
  }

  try {
    await feeStructureStore.deleteFeeStructure(feeStructure.id)
    loadFeeStructures() // Reload to reflect changes
  } catch (err) {
    console.error('Failed to delete fee structure:', err)
    alert('Failed to delete fee structure. Please try again.')
  }
}

function getRowClass(feeStructure: FeeStructure) {
  return feeStructure.is_active ? '' : 'row-inactive'
}

function formatCurrency(amount: number): string {
  return amount.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function hasSiblingDiscounts(feeStructure: FeeStructure): boolean {
  return (
    feeStructure.sibling_2_discount > 0 ||
    feeStructure.sibling_3_discount > 0 ||
    feeStructure.sibling_4_plus_discount > 0
  )
}

function hasPaymentDiscounts(feeStructure: FeeStructure): boolean {
  return (
    feeStructure.yearly_discount > 0 ||
    feeStructure.monthly_discount > 0 ||
    feeStructure.weekly_discount > 0
  )
}

// Lifecycle
onMounted(() => {
  loadFeeStructures()
  loadStatistics()
})
</script>

<style scoped>
.fee-structures-list {
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #111827;
}

.filters {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
}

.filter-actions {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
}

.loading,
.error-message {
  padding: 2rem;
  text-align: center;
}

.error-message {
  color: #dc2626;
  background: #fee2e2;
  border-radius: 8px;
}

.fee-structures-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.fee-structures-table {
  width: 100%;
  border-collapse: collapse;
}

.fee-structures-table th,
.fee-structures-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.fee-structures-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.fee-structures-table tbody tr:hover {
  background: #f9fafb;
}

.row-inactive {
  opacity: 0.6;
  background: #f3f4f6;
}

.grade-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.academic-year {
  font-weight: 500;
  color: #111827;
}

.tuition-amount {
  font-weight: 600;
  color: #059669;
  font-size: 1.125rem;
}

.frequency-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.frequency-item {
  font-size: 0.875rem;
}

.freq-label {
  color: #6b7280;
  margin-right: 0.25rem;
}

.freq-value {
  font-weight: 500;
  color: #111827;
}

.discount-hint {
  color: #059669;
  font-size: 0.75rem;
  margin-left: 0.25rem;
}

.discount-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.discount-item {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: #d1fae5;
  color: #065f46;
  border-radius: 4px;
}

.text-muted {
  color: #9ca3af;
  font-size: 0.875rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
}

.status-inactive {
  background: #f3f4f6;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.empty-state {
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 8px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Button Styles */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
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

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-link {
  background: transparent;
  color: #6366f1;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}
</style>
