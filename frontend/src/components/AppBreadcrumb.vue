<template>
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <ol class="breadcrumb-list">
      <li
        v-for="(crumb, index) in breadcrumbs"
        :key="crumb.path"
        class="breadcrumb-item"
      >
        <!-- Not last item - make it a link -->
        <router-link
          v-if="index < breadcrumbs.length - 1"
          :to="crumb.path"
          class="breadcrumb-link"
        >
          {{ crumb.label }}
        </router-link>

        <!-- Last item - current page -->
        <span v-else class="breadcrumb-current">
          {{ crumb.label }}
        </span>

        <!-- Separator -->
        <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-separator">
          /
        </span>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface Breadcrumb {
  label: string
  path: string
}

const route = useRoute()

/**
 * Generate breadcrumbs from current route
 */
const breadcrumbs = computed((): Breadcrumb[] => {
  const crumbs: Breadcrumb[] = []
  const pathSegments = route.path.split('/').filter(Boolean)

  // Always start with home
  crumbs.push({
    label: 'Home',
    path: '/'
  })

  // Build path incrementally
  let currentPath = ''

  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`

    // Check if this is a UUID (user ID, etc.)
    const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(segment)

    // Skip UUIDs in breadcrumb display (they're not user-friendly)
    if (isUUID) {
      // For UUIDs, show "View" or "Edit" based on next segment
      const nextSegment = pathSegments[index + 1]
      if (nextSegment === 'edit') {
        crumbs.push({
          label: 'Edit',
          path: currentPath + '/edit'
        })
        return // Skip the actual "edit" segment
      } else {
        crumbs.push({
          label: 'View',
          path: currentPath
        })
        return
      }
    }

    // Skip "edit" if we already handled it
    if (segment === 'edit' && pathSegments[index - 1] && /^[0-9a-f-]{36}$/i.test(pathSegments[index - 1])) {
      return
    }

    // Convert segment to readable label
    const label = formatSegmentLabel(segment)

    crumbs.push({
      label,
      path: currentPath
    })
  })

  return crumbs
})

/**
 * Format path segment to readable label
 */
function formatSegmentLabel(segment: string): string {
  // Handle special cases
  const labelMap: Record<string, string> = {
    'users': 'Users',
    'create': 'Create',
    'edit': 'Edit',
    'statistics': 'Statistics',
    'dashboard': 'Dashboard',
    'profile': 'Profile',
    'settings': 'Settings'
  }

  if (labelMap[segment]) {
    return labelMap[segment]
  }

  // Default: capitalize first letter and replace hyphens
  return segment
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
</script>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.breadcrumb-link {
  color: #42b883;
  text-decoration: none;
  transition: color 0.2s, text-decoration 0.2s;
}

.breadcrumb-link:hover {
  color: #35a372;
  text-decoration: underline;
}

.breadcrumb-current {
  color: #6c757d;
  font-weight: 500;
}

.breadcrumb-separator {
  color: #dee2e6;
  user-select: none;
}

@media (max-width: 768px) {
  .breadcrumb-item {
    font-size: 0.85rem;
  }
}
</style>
