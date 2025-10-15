<template>
  <div class="base-table-container">
    <!-- Table -->
    <table class="base-table">
      <!-- Header -->
      <thead>
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            :class="{ 'sortable': column.sortable }"
            @click="column.sortable ? handleSort(column.key) : null"
          >
            <div class="th-content">
              <span>{{ column.label }}</span>
              <span v-if="column.sortable" class="sort-icon">
                <span v-if="sortKey === column.key">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
                <span v-else class="sort-icon-inactive">⇅</span>
              </span>
            </div>
          </th>
          <th v-if="hasActions" class="actions-column">Actions</th>
        </tr>
      </thead>

      <!-- Body -->
      <tbody>
        <!-- Empty State -->
        <tr v-if="data.length === 0" class="empty-row">
          <td :colspan="columns.length + (hasActions ? 1 : 0)">
            <slot name="empty">
              <div class="empty-state">
                <p>No data available</p>
              </div>
            </slot>
          </td>
        </tr>

        <!-- Data Rows -->
        <tr
          v-for="(row, index) in data"
          :key="getRowKey(row, index)"
          :class="{ 'row-clickable': rowClickable }"
          @click="handleRowClick(row)"
        >
          <td v-for="column in columns" :key="column.key">
            <!-- Custom cell slot -->
            <slot
              v-if="$slots[`cell-${column.key}`]"
              :name="`cell-${column.key}`"
              :row="row"
              :column="column"
              :value="getCellValue(row, column.key)"
            ></slot>
            <!-- Default cell rendering -->
            <span v-else>{{ getCellValue(row, column.key) }}</span>
          </td>

          <!-- Actions Column -->
          <td v-if="hasActions" class="actions-cell">
            <slot name="actions" :row="row"></slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface TableColumn {
  key: string
  label: string
  sortable?: boolean
}

interface Props {
  columns: TableColumn[]
  data: any[]
  rowKey?: string
  rowClickable?: boolean
  hasActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  rowKey: 'id',
  rowClickable: false,
  hasActions: false
})

const emit = defineEmits<{
  (e: 'row-click', row: any): void
  (e: 'sort', key: string, order: 'asc' | 'desc'): void
}>()

const sortKey = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')

/**
 * Get row key
 */
function getRowKey(row: any, index: number): string | number {
  return row[props.rowKey] || index
}

/**
 * Get cell value by key
 */
function getCellValue(row: any, key: string): any {
  // Support nested keys with dot notation (e.g., 'user.name')
  return key.split('.').reduce((obj, k) => obj?.[k], row)
}

/**
 * Handle sort
 */
function handleSort(key: string) {
  if (sortKey.value === key) {
    // Toggle sort order
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    // New sort column
    sortKey.value = key
    sortOrder.value = 'asc'
  }

  emit('sort', key, sortOrder.value)
}

/**
 * Handle row click
 */
function handleRowClick(row: any) {
  if (props.rowClickable) {
    emit('row-click', row)
  }
}
</script>

<style scoped>
.base-table-container {
  width: 100%;
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.base-table {
  width: 100%;
  border-collapse: collapse;
}

.base-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.base-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
  white-space: nowrap;
}

.base-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.base-table th.sortable:hover {
  background: #e9ecef;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-icon {
  display: inline-flex;
  font-size: 0.7rem;
  color: #42b883;
}

.sort-icon-inactive {
  color: #9e9e9e;
  opacity: 0.5;
}

.base-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  color: #2c3e50;
}

.base-table tbody tr:hover {
  background: #f8f9fa;
}

.base-table tbody tr:last-child td {
  border-bottom: none;
}

.row-clickable {
  cursor: pointer;
}

.actions-column,
.actions-cell {
  width: 120px;
  text-align: center;
}

.empty-row td {
  padding: 3rem;
}

.empty-state {
  text-align: center;
  color: #6c757d;
}

.empty-state p {
  margin: 0;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .base-table th,
  .base-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.85rem;
  }
}
</style>
