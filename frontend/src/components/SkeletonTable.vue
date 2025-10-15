<template>
  <div class="skeleton-table">
    <!-- Table Header -->
    <div class="skeleton-table-header">
      <BaseSkeleton
        v-for="i in columns"
        :key="`header-${i}`"
        variant="text"
        height="1.2rem"
        :width="getColumnWidth(i)"
      />
    </div>

    <!-- Table Rows -->
    <div
      v-for="row in rows"
      :key="`row-${row}`"
      class="skeleton-table-row"
    >
      <BaseSkeleton
        v-for="col in columns"
        :key="`cell-${row}-${col}`"
        variant="text"
        height="1rem"
        :width="getColumnWidth(col)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseSkeleton from './BaseSkeleton.vue'

interface Props {
  rows?: number
  columns?: number
  columnWidths?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  rows: 5,
  columns: 4
})

/**
 * Get column width
 */
function getColumnWidth(index: number): string {
  if (props.columnWidths && props.columnWidths[index - 1]) {
    return props.columnWidths[index - 1]
  }
  // Vary widths slightly for more realistic look
  const widths = ['90%', '80%', '85%', '75%', '95%']
  return widths[(index - 1) % widths.length]
}
</script>

<style scoped>
.skeleton-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.skeleton-table-header {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 1rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-bottom: 2px solid #e0e0e0;
}

.skeleton-table-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 1rem;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.skeleton-table-row:last-child {
  border-bottom: none;
}
</style>
