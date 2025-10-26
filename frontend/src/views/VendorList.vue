<template>
  <div class="vendor-list">
    <div class="page-header">
      <h1>Vendors</h1>
      <button @click="handleCreate" class="btn btn-primary">
        Create Vendor
      </button>
    </div>

    <!-- Statistics Cards -->
    <div v-if="statistics" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total Vendors</div>
        <div class="stat-value">{{ statistics.total_vendors }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Active Vendors</div>
        <div class="stat-value">{{ statistics.active_vendors }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Preferred Vendors</div>
        <div class="stat-value">{{ statistics.preferred_vendors }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Rating</div>
        <div class="stat-value">{{ statistics.average_rating.toFixed(2) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Contract Value</div>
        <div class="stat-value">${{ formatCurrency(statistics.total_contract_value) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Expiring Contracts</div>
        <div class="stat-value" :class="{ 'text-warning': statistics.expiring_contracts > 0 }">
          {{ statistics.expiring_contracts }}
        </div>
      </div>
    </div>

    <!-- Alerts -->
    <div v-if="alerts && (alerts.expiring_contracts.length > 0 || alerts.expired_insurance.length > 0)" class="alerts-section">
      <div v-if="alerts.expiring_contracts.length > 0" class="alert alert-warning">
        <strong>⚠️ {{ alerts.expiring_contracts.length }} Contract(s) Expiring Soon:</strong>
        <ul>
          <li v-for="alert in alerts.expiring_contracts.slice(0, 3)" :key="alert.vendor_id">
            {{ alert.company_name }} ({{ alert.days_until_expiry }} days)
          </li>
        </ul>
      </div>
      <div v-if="alerts.expired_insurance.length > 0" class="alert alert-danger">
        <strong>🚨 {{ alerts.expired_insurance.length }} Expired Insurance:</strong>
        <ul>
          <li v-for="alert in alerts.expired_insurance.slice(0, 3)" :key="alert.vendor_id">
            {{ alert.company_name }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>Vendor Type</label>
        <select v-model="localFilters.vendor_type">
          <option value="">All Types</option>
          <option value="food_service">Food Service</option>
          <option value="supplies">Supplies</option>
          <option value="maintenance">Maintenance</option>
          <option value="it_services">IT Services</option>
          <option value="transportation">Transportation</option>
          <option value="events">Events</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Status</label>
        <select v-model="localFilters.vendor_status">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
          <option value="terminated">Terminated</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Search</label>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search vendors..."
          @keyup.enter="handleSearch"
        />
      </div>

      <div class="filter-actions">
        <button @click="applyFilters" class="btn btn-secondary">Apply Filters</button>
        <button @click="clearFilters" class="btn btn-link">Clear</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">Loading vendors...</div>

    <!-- Error State -->
    <div v-if="error" class="error-message">{{ error }}</div>

    <!-- Vendors Table -->
    <div v-if="!loading && vendors.length > 0" class="vendors-table-container">
      <table class="vendors-table">
        <thead>
          <tr>
            <th>Company Name</th>
            <th>Type</th>
            <th>Contact</th>
            <th>Status</th>
            <th>Rating</th>
            <th>Contract</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="vendor in vendors" :key="vendor.id">
            <td>
              <div class="vendor-name">
                <div class="name-text">
                  {{ vendor.company_name }}
                  <span v-if="vendor.preferred" class="preferred-badge">⭐</span>
                </div>
                <div v-if="vendor.category" class="category-text">{{ vendor.category }}</div>
              </div>
            </td>
            <td>
              <span class="vendor-type-badge">
                {{ formatVendorType(vendor.vendor_type) }}
              </span>
            </td>
            <td>
              <div class="contact-info">
                <div v-if="vendor.primary_contact_name">{{ vendor.primary_contact_name }}</div>
                <div v-if="vendor.email" class="contact-email">{{ vendor.email }}</div>
                <div v-if="vendor.phone" class="contact-phone">{{ vendor.phone }}</div>
              </div>
            </td>
            <td>
              <span class="status-badge" :class="`status-${vendor.status}`">
                {{ formatStatus(vendor.status) }}
              </span>
              <div v-if="vendor.contract_expiring_soon" class="warning-text">⚠️ Contract Expiring</div>
              <div v-if="vendor.insurance_expired" class="danger-text">🚨 Insurance Expired</div>
            </td>
            <td>
              <div class="rating">
                <span v-if="vendor.performance_rating">
                  ⭐ {{ vendor.performance_rating.toFixed(1) }}
                </span>
                <span v-else class="text-muted">No rating</span>
              </div>
            </td>
            <td>
              <div class="contract-info">
                <div v-if="vendor.contract_value">
                  ${{ formatCurrency(vendor.contract_value) }}
                </div>
                <div v-if="vendor.contract_end_date" class="contract-date">
                  Ends: {{ formatDate(vendor.contract_end_date) }}
                </div>
              </div>
            </td>
            <td>
              <div class="action-buttons">
                <button
                  @click="handleView(vendor.id)"
                  class="btn btn-sm btn-secondary"
                  title="View Details"
                >
                  View
                </button>
                <button
                  @click="handleEdit(vendor.id)"
                  class="btn btn-sm btn-secondary"
                >
                  Edit
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && vendors.length === 0" class="empty-state">
      <p>No vendors found.</p>
      <button @click="handleCreate" class="btn btn-primary">Create Your First Vendor</button>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn btn-secondary"
      >
        Previous
      </button>
      <span class="pagination-info">
        Page {{ currentPage }} of {{ totalPages }} ({{ totalVendors }} total)
      </span>
      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="btn btn-secondary"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useVendorStore } from '@/stores/vendorStore'
import type { VendorFilters } from '@/types/vendor'

const router = useRouter()
const vendorStore = useVendorStore()

// Hardcoded school ID for demo (should come from auth context)
const SCHOOL_ID = '60da2256-81fc-4ca5-bf6b-467b8d371c61'

// Local state
const localFilters = ref<VendorFilters>({})
const searchQuery = ref('')

// Computed from store
const vendors = computed(() => vendorStore.vendors)
const loading = computed(() => vendorStore.loading)
const error = computed(() => vendorStore.error)
const statistics = computed(() => vendorStore.statistics)
const alerts = computed(() => vendorStore.alerts)
const currentPage = computed(() => vendorStore.currentPage)
const totalPages = computed(() => vendorStore.totalPages)
const totalVendors = computed(() => vendorStore.totalVendors)

// Methods
async function loadData() {
  try {
    await Promise.all([
      vendorStore.fetchVendors(SCHOOL_ID, localFilters.value),
      vendorStore.fetchStatistics(SCHOOL_ID),
      vendorStore.fetchAlerts(SCHOOL_ID),
    ])
  } catch (err) {
    console.error('Failed to load vendor data:', err)
  }
}

function applyFilters() {
  loadData()
}

function clearFilters() {
  localFilters.value = {}
  searchQuery.value = ''
  vendorStore.clearFilters()
  loadData()
}

async function handleSearch() {
  if (searchQuery.value.trim()) {
    try {
      await vendorStore.searchVendors(SCHOOL_ID, searchQuery.value.trim())
    } catch (err) {
      console.error('Search failed:', err)
    }
  } else {
    loadData()
  }
}

function goToPage(page: number) {
  vendorStore.setPage(page)
  loadData()
}

function handleCreate() {
  // TODO: Navigate to create form or open modal
  console.log('Create vendor')
}

function handleView(vendorId: string) {
  // TODO: Navigate to vendor detail view
  console.log('View vendor:', vendorId)
}

function handleEdit(vendorId: string) {
  // TODO: Navigate to edit form
  console.log('Edit vendor:', vendorId)
}

// Formatting helpers
function formatVendorType(type: string): string {
  const types: Record<string, string> = {
    food_service: 'Food Service',
    supplies: 'Supplies',
    maintenance: 'Maintenance',
    it_services: 'IT Services',
    transportation: 'Transportation',
    events: 'Events',
    other: 'Other',
  }
  return types[type] || type
}

function formatStatus(status: string): string {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

function formatCurrency(value: number): string {
  return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.vendor-list {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a202c;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 14px;
  color: #718096;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
}

.alerts-section {
  margin-bottom: 24px;
}

.alert {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.alert-warning {
  background-color: #fef3c7;
  border-left: 4px solid #f59e0b;
}

.alert-danger {
  background-color: #fee2e2;
  border-left: 4px solid #ef4444;
}

.alert ul {
  margin: 8px 0 0 20px;
}

.filters {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 8px;
}

.filter-group select,
.filter-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.loading,
.error-message {
  text-align: center;
  padding: 40px;
  font-size: 16px;
}

.error-message {
  color: #e53e3e;
}

.vendors-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.vendors-table {
  width: 100%;
  border-collapse: collapse;
}

.vendors-table thead {
  background-color: #f7fafc;
  border-bottom: 2px solid #e2e8f0;
}

.vendors-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.vendors-table td {
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.vendor-name .name-text {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
}

.vendor-name .category-text {
  font-size: 12px;
  color: #718096;
}

.preferred-badge {
  margin-left: 6px;
}

.vendor-type-badge {
  display: inline-block;
  padding: 4px 12px;
  background-color: #e2e8f0;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: #2d3748;
}

.contact-info {
  font-size: 13px;
}

.contact-email,
.contact-phone {
  color: #718096;
  font-size: 12px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-active {
  background-color: #d1fae5;
  color: #065f46;
}

.status-inactive {
  background-color: #e2e8f0;
  color: #4a5568;
}

.status-suspended {
  background-color: #fed7d7;
  color: #c53030;
}

.status-terminated {
  background-color: #fecaca;
  color: #991b1b;
}

.warning-text {
  font-size: 11px;
  color: #d97706;
  margin-top: 4px;
}

.danger-text {
  font-size: 11px;
  color: #dc2626;
  margin-top: 4px;
}

.text-warning {
  color: #d97706;
}

.rating {
  font-size: 14px;
}

.contract-info {
  font-size: 13px;
}

.contract-date {
  color: #718096;
  font-size: 12px;
  margin-top: 4px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #e2e8f0;
  color: #2d3748;
}

.btn-secondary:hover {
  background-color: #cbd5e0;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.btn-link {
  background: none;
  color: #3b82f6;
}

.btn-link:hover {
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.empty-state p {
  font-size: 18px;
  color: #718096;
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.pagination-info {
  font-size: 14px;
  color: #718096;
}

.text-muted {
  color: #a0aec0;
}
</style>
