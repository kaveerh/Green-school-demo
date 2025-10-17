<template>
  <div class="parent-list">
    <!-- Header -->
    <div class="list-header">
      <h2>Parent Management</h2>
      <button @click="goToCreate" class="btn-primary">
        <span class="icon">➕</span>
        Create Parent
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="search-filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search parents by name, email, phone, or occupation..."
          @input="handleSearch"
          class="search-input"
        />
        <span v-if="searchQuery" @click="clearSearch" class="clear-btn">✕</span>
      </div>

      <div class="filters">
        <label class="filter-checkbox">
          <input type="checkbox" v-model="filters.emergencyContact" @change="applyFilters" />
          Emergency Contacts Only
        </label>
        <label class="filter-checkbox">
          <input type="checkbox" v-model="filters.pickupAuthorized" @change="applyFilters" />
          Pickup Authorized Only
        </label>
        <label class="filter-checkbox">
          <input type="checkbox" v-model="filters.newsletterSubscribers" @change="applyFilters" />
          Newsletter Subscribers Only
        </label>
      </div>
    </div>

    <!-- Statistics Summary -->
    <div v-if="statistics" class="statistics-summary">
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_parents }}</div>
        <div class="stat-label">Total Parents</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.emergency_contacts }}</div>
        <div class="stat-label">Emergency Contacts</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.pickup_authorized }}</div>
        <div class="stat-label">Pickup Authorized</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.parents_with_children }}</div>
        <div class="stat-label">With Children</div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="parentStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading parents...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="parentStore.error" class="error-banner">
      {{ parentStore.error }}
      <button @click="parentStore.clearError" class="btn-text">Dismiss</button>
    </div>

    <!-- Parents Table -->
    <div v-else-if="parentStore.parents.length > 0" class="table-container">
      <table class="parents-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Contact Info</th>
            <th>Occupation</th>
            <th>Children</th>
            <th>Preferences</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="parent in parentStore.parents" :key="parent.id">
            <td>
              <div class="parent-name">
                {{ formatParentName(parent) }}
              </div>
              <div v-if="parent.user?.email" class="parent-email">
                {{ parent.user.email }}
              </div>
            </td>
            <td>
              <div class="contact-info">
                <div v-if="parent.phone_mobile" class="contact-item">
                  📱 {{ parent.phone_mobile }}
                </div>
                <div v-if="parent.phone_work" class="contact-item">
                  💼 {{ parent.phone_work }}
                </div>
                <div v-if="parent.preferred_contact_method" class="preferred-method">
                  Prefers: {{ getContactMethodLabel(parent.preferred_contact_method) }}
                </div>
              </div>
            </td>
            <td>
              <div v-if="parent.occupation" class="occupation">
                {{ parent.occupation }}
              </div>
              <div v-if="parent.workplace" class="workplace">
                {{ parent.workplace }}
              </div>
            </td>
            <td>
              <div class="children-count">
                {{ getChildrenCount(parent) }} {{ getChildrenCount(parent) === 1 ? 'child' : 'children' }}
              </div>
            </td>
            <td>
              <div class="preferences">
                <span v-if="parent.emergency_contact" class="badge badge-emergency" title="Emergency Contact">
                  🚨 Emergency
                </span>
                <span v-if="parent.pickup_authorized" class="badge badge-pickup" title="Pickup Authorized">
                  🚗 Pickup
                </span>
                <span v-if="parent.receives_newsletter" class="badge badge-newsletter" title="Newsletter Subscriber">
                  📧 Newsletter
                </span>
              </div>
            </td>
            <td>
              <div class="actions">
                <button @click="viewParent(parent.id)" class="btn-icon" title="View Details">
                  👁️
                </button>
                <button @click="editParent(parent.id)" class="btn-icon" title="Edit">
                  ✏️
                </button>
                <button @click="confirmDelete(parent)" class="btn-icon btn-danger" title="Delete">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">👨‍👩‍👧‍👦</div>
      <h3>No Parents Found</h3>
      <p v-if="searchQuery">No parents match your search criteria.</p>
      <p v-else>Get started by creating your first parent profile.</p>
      <button @click="goToCreate" class="btn-primary">
        Create Parent
      </button>
    </div>

    <!-- Pagination -->
    <div v-if="parentStore.totalParents > parentStore.pageSize" class="pagination">
      <button
        @click="parentStore.previousPage"
        :disabled="!parentStore.hasPreviousPage"
        class="btn-secondary"
      >
        ← Previous
      </button>
      <span class="page-info">
        Page {{ parentStore.currentPage }} of {{ parentStore.totalPages }}
        ({{ parentStore.totalParents }} total)
      </span>
      <button
        @click="parentStore.nextPage"
        :disabled="!parentStore.hasNextPage"
        class="btn-secondary"
      >
        Next →
      </button>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteConfirmation" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content" @click.stop>
        <h3>Confirm Delete</h3>
        <p>
          Are you sure you want to delete parent
          <strong>{{ deleteConfirmation ? formatParentName(deleteConfirmation) : '' }}</strong>?
        </p>
        <p class="warning">This will also remove all relationships with students.</p>
        <div class="modal-actions">
          <button @click="cancelDelete" class="btn-secondary">Cancel</button>
          <button @click="executeDelete" class="btn-danger">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useParentStore } from '@/stores/parentStore'
import type { Parent } from '@/types/parent'
import {
  formatParentName,
  getContactMethodLabel
} from '@/types/parent'

const router = useRouter()
const parentStore = useParentStore()

const searchQuery = ref('')
const filters = ref({
  emergencyContact: false,
  pickupAuthorized: false,
  newsletterSubscribers: false
})
const statistics = ref(null)
const deleteConfirmation = ref<Parent | null>(null)

onMounted(async () => {
  await loadParents()
  await loadStatistics()
})

async function loadParents() {
  try {
    await parentStore.fetchParents()
  } catch (error) {
    console.error('Failed to load parents:', error)
  }
}

async function loadStatistics() {
  try {
    const stats = await parentStore.fetchStatistics()
    statistics.value = stats
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

async function handleSearch() {
  if (searchQuery.value.trim().length >= 2) {
    try {
      await parentStore.searchParents(searchQuery.value.trim())
    } catch (error) {
      console.error('Search failed:', error)
    }
  } else if (searchQuery.value.trim().length === 0) {
    await loadParents()
  }
}

function clearSearch() {
  searchQuery.value = ''
  loadParents()
}

async function applyFilters() {
  // TODO: Implement filter logic
  // For now, just reload
  await loadParents()
}

function goToCreate() {
  router.push('/parents/create')
}

function viewParent(id: string) {
  router.push(`/parents/${id}`)
}

function editParent(id: string) {
  router.push(`/parents/${id}/edit`)
}

function confirmDelete(parent: Parent) {
  deleteConfirmation.value = parent
}

function cancelDelete() {
  deleteConfirmation.value = null
}

async function executeDelete() {
  if (!deleteConfirmation.value) return

  try {
    await parentStore.deleteParent(deleteConfirmation.value.id)
    deleteConfirmation.value = null
    await loadStatistics() // Refresh stats
  } catch (error) {
    console.error('Failed to delete parent:', error)
  }
}

function getChildrenCount(parent: Parent): number {
  return parent.children?.length || 0
}
</script>

<style scoped>
.parent-list {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.list-header h2 {
  margin: 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.search-filters {
  margin-bottom: 2rem;
}

.search-box {
  position: relative;
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #42b883;
}

.clear-btn {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #999;
  font-size: 1.25rem;
}

.clear-btn:hover {
  color: #666;
}

.filters {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.filter-checkbox input[type="checkbox"] {
  cursor: pointer;
}

.statistics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #42b883;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.parents-table {
  width: 100%;
  border-collapse: collapse;
}

.parents-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e0e0e0;
}

.parents-table td {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.parents-table tbody tr:hover {
  background: #f8f9fa;
}

.parent-name {
  font-weight: 500;
  color: #2c3e50;
}

.parent-email {
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.contact-item {
  font-size: 0.9rem;
  color: #495057;
}

.preferred-method {
  font-size: 0.8rem;
  color: #42b883;
  margin-top: 0.25rem;
}

.occupation {
  font-weight: 500;
  color: #495057;
}

.workplace {
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.children-count {
  font-weight: 500;
  color: #495057;
}

.preferences {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-emergency {
  background: #ffebee;
  color: #c62828;
}

.badge-pickup {
  background: #e3f2fd;
  color: #1565c0;
}

.badge-newsletter {
  background: #f3e5f5;
  color: #6a1b9a;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: #e0e0e0;
}

.btn-danger {
  color: #c62828;
}

.btn-danger:hover {
  background: #ffebee;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #35a372;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: white;
  color: #42b883;
  border: 1px solid #42b883;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background: #42b883;
  color: white;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-text {
  background: none;
  border: none;
  color: #42b883;
  cursor: pointer;
  text-decoration: underline;
  margin-left: 1rem;
}

.loading-spinner,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b883;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-banner {
  background: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0.5rem 0;
  color: #2c3e50;
}

.empty-state p {
  color: #6c757d;
  margin-bottom: 1.5rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem;
}

.page-info {
  color: #6c757d;
  font-size: 0.9rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
}

.modal-content h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.modal-content p {
  color: #495057;
  margin-bottom: 1rem;
}

.warning {
  color: #c62828;
  font-weight: 500;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>
